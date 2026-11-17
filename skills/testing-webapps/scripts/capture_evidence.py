#!/usr/bin/env python3
"""
Capture the 8-shot evidence bundle used by the design/review skills, plus the
objective DOM measurements a review needs.

Shots: first-view, full-page, mobile, dark, empty, loading, error, focus.
Measures: console errors, horizontal overflow, distinct font-size/family/
          border-radius/box-shadow/padding/color values.

The empty/loading/error shots are driven by Playwright route mocks so they
capture the app's real rendered state — not a faked class. For state shots
that depend on user data (e.g. a first-run empty state), pass the extra
setup steps to your own script and use this one for the rest.

Usage:
    # Full bundle for a running app
    python scripts/capture_evidence.py --url http://localhost:5173 --out /tmp/evidence

    # Only the happy-path shots (static HTML, no data endpoints to mock)
    python scripts/capture_evidence.py --url file:///abs/path/index.html --shots first,full,mobile,dark,focus

    # Specify which API path feeds the main data view
    python scripts/capture_evidence.py --url http://localhost:5173 --data-api "**/api/items"

Requires the opencode venv (playwright). Run --help for all options.
"""

import argparse
import json
import os
import sys


def run_capture(args):
    # Keep this in a nested function so the playwright import only happens
    # when we actually capture (not on --help).
    from playwright.sync_api import sync_playwright

    url = args.url
    out = args.out
    os.makedirs(out, exist_ok=True)
    shots_wanted = set(args.shots.split(","))
    data_api = args.data_api
    is_file_url = url.startswith("file://")

    # Route mocks only intercept http/https — not file://. If state shots are
    # requested against a file:// URL, they would silently capture the app's
    # natural state (usually error), not the mocked empty/loading state. Warn.
    state_shots = shots_wanted & {"empty", "loading", "error"}
    if state_shots and is_file_url:
        print(f"WARNING: --shots includes {sorted(state_shots)} but --url is file://.")
        print("         Playwright page.route() cannot intercept file:// requests,")
        print("         so these shots will capture the app's NATURAL state (often error),")
        print("         not a mocked empty/loading state. Use an HTTP server for true state shots.")
        print()

    results = {"shots": {}, "console_errors": [], "overflow": [], "distinct": {}, "scale": 2}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        page = context.new_page()

        page.on("console", lambda m: m.type == "error" and results["console_errors"].append(m.text))
        page.on("pageerror", lambda e: results["console_errors"].append(f"uncaught: {e}"))

        def settle():
            # Fonts must be loaded or the screenshot reviews the fallback, not the design.
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(250)

        def shot(name, full_page=False):
            settle()
            path = os.path.join(out, f"{name}.png")
            page.screenshot(path=path, full_page=full_page)
            results["shots"][name] = path
            print(f"  shot: {name}")

        def measure_distinct():
            results["distinct"] = {
                prop: page.evaluate(
                    """(p) => [...new Set([...document.querySelectorAll('*')]
                        .map(e => getComputedStyle(e)[p]))].filter(v => v && v!=='none' && v!=='0px')""",
                    prop,
                )
                for prop in ["font-size", "font-family", "border-radius", "box-shadow", "padding", "color"]
            }
            for prop, vals in results["distinct"].items():
                print(f"  distinct {prop}: {len(vals)}")

        def measure_overflow():
            results["overflow"] = page.evaluate(
                """() => [...document.querySelectorAll('*')]
                    .filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1)
                    .slice(0, 10).map(e => e.tagName + '.' + e.className)"""
            )
            print(f"  overflow: {len(results['overflow'])}")

        # --- happy path load ---
        page.goto(url)
        page.wait_for_load_state("networkidle")

        if "first" in shots_wanted:
            shot("first-view")
        if "full" in shots_wanted:
            shot("full-page", full_page=True)

        if "mobile" in shots_wanted:
            page.set_viewport_size({"width": 390, "height": 844})
            shot("mobile", full_page=True)
            page.set_viewport_size({"width": 1440, "height": 900})

        if "dark" in shots_wanted:
            page.emulate_media(color_scheme="dark")
            shot("dark")
            page.emulate_media(color_scheme=None)

        # --- state shots (reload each so the route mock is in effect on fetch) ---
        if "empty" in shots_wanted and data_api:
            page.route(data_api, lambda r: r.fulfill(status=200, json=[]))
            page.reload(); page.wait_for_load_state("networkidle")
            shot("empty")
            page.unroute(data_api)

        if "loading" in shots_wanted and data_api:
            import time

            def slow(route):
                time.sleep(3)   # hold the response so the skeleton stays up
                route.continue_()
            page.route(data_api, slow)
            page.reload(); page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(800)  # mid-load, while the skeleton is up
            shot("loading")
            page.wait_for_load_state("networkidle")
            page.unroute(data_api)

        if "error" in shots_wanted and data_api:
            page.route(data_api, lambda r: r.fulfill(status=500))
            page.reload(); page.wait_for_load_state("networkidle")
            shot("error")
            page.unroute(data_api)

        if "focus" in shots_wanted:
            page.goto(url); page.wait_for_load_state("networkidle")
            page.keyboard.press("Tab"); page.keyboard.press("Tab"); page.keyboard.press("Tab")
            shot("focus")

        # --- objective measurements on the canonical (light, happy-path) state ---
        page.emulate_media(color_scheme=None)
        page.goto(url); page.wait_for_load_state("networkidle")
        measure_distinct()
        measure_overflow()

        browser.close()

    out_json = os.path.join(out, "measurements.json")
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results['shots'])} shots + measurements.json to {out}")
    print(f"  console errors: {len(results['console_errors'])}")
    for e in results["console_errors"][:10]:
        print(f"    - {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Capture the 8-shot evidence bundle + DOM measurements for a UI review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--url", required=True, help="URL or file:// path to capture")
    parser.add_argument("--out", default="/tmp/evidence", help="Output directory (default: /tmp/evidence)")
    parser.add_argument(
        "--shots",
        default="first,full,mobile,dark,empty,loading,error,focus",
        help="Comma-separated subset of: first,full,mobile,dark,empty,loading,error,focus",
    )
    parser.add_argument(
        "--data-api",
        default=None,
        help="GLOB pattern of the API that feeds the main data view. Required for empty/loading/error shots.",
    )
    args = parser.parse_args()

    if any(s in args.shots for s in ("empty", "loading", "error")) and not args.data_api:
        print("Warning: empty/loading/error shots need --data-api to know which endpoint to mock. They will be skipped.")
        args.shots = ",".join(s for s in args.shots.split(",") if s not in ("empty", "loading", "error"))

    run_capture(args)


if __name__ == "__main__":
    main()
