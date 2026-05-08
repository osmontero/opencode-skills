#!/usr/bin/env python3
"""Create test images for the processing-images skill."""

from PIL import Image, ImageDraw, ImageFont

def create_error_screenshot():
    """Create a fake error message screenshot."""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a reasonable font size
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        error_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except:
        font = ImageFont.load_default()
        error_font = font
    
    y = 50
    draw.text((20, y), "Error Report", fill='red', font=error_font)
    y += 40
    
    messages = [
        "Traceback (most recent call last):",
        "  File \"/app/main.py\", line 42, in <module>",
        "    process_data(data)",
        "  File \"/app/utils.py\", line 15, in process_data",
        "    return json.loads(input_string)",
        "json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)",
        "",
        "Error Code: JSON_PARSE_ERROR",
        "Timestamp: 2024-01-15 14:32:18",
        "Request ID: req_abc123def456"
    ]
    
    for msg in messages:
        draw.text((20, y), msg, fill='black', font=font)
        y += 25
    
    img.save('test_images/error_screenshot.png')
    print("Created error_screenshot.png")

def create_sales_chart():
    """Create a simple sales chart."""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    except:
        font = ImageFont.load_default()
        title_font = font
    
    # Title
    draw.text((280, 20), "Monthly Sales Data 2024", fill='black', font=title_font)
    
    # Chart area
    margin_left = 80
    margin_top = 80
    chart_width = 600
    chart_height = 400
    
    # Draw axes
    draw.line([(margin_left, margin_top), (margin_left, margin_top + chart_height)], fill='black', width=2)
    draw.line([(margin_left, margin_top + chart_height), (margin_left + chart_width, margin_top + chart_height)], fill='black', width=2)
    
    # Data: months and sales
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    sales = [45000, 52000, 48000, 61000, 58000, 72000]
    max_sales = 80000
    
    bar_width = 80
    bar_spacing = 60
    
    for i, (month, value) in enumerate(zip(months, sales)):
        bar_height = int((value / max_sales) * chart_height)
        x = margin_left + 60 + i * (bar_width + bar_spacing)
        
        # Draw bar
        draw.rectangle([
            x, margin_top + chart_height - bar_height,
            x + bar_width, margin_top + chart_height
        ], fill='steelblue' if i % 2 == 0 else 'dodgerblue')
        
        # Month label
        draw.text((x + 20, margin_top + chart_height + 10), month, fill='black', font=font)
        
        # Value on top of bar
        draw.text((x + 15, margin_top + chart_height - bar_height - 25), 
                  f"${value/1000}k", fill='black', font=font)
    
    # Y-axis label
    draw.text((10, margin_top + 150), "Sales ($)", fill='black', font=font)
    
    img.save('test_images/sales_chart.png')
    print("Created sales_chart.png")

def create_receipt():
    """Create a fake receipt image."""
    width, height = 500, 700
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        bold_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except:
        font = ImageFont.load_default()
        bold_font = font
        small_font = font
    
    y = 30
    
    # Header
    draw.text((150, y), "TECH SUPPLIES INC.", fill='black', font=bold_font)
    y += 25
    draw.text((180, y), "123 Main Street", fill='black', font=font)
    y += 20
    draw.text((180, y), "San Francisco, CA 94102", fill='black', font=font)
    y += 20
    draw.text((180, y), "Phone: (415) 555-0123", fill='black', font=font)
    y += 40
    
    # Receipt info
    draw.text((20, y), "Date: 2024-01-15", fill='black', font=font)
    draw.text((300, y), "Receipt #: 12345", fill='black', font=font)
    y += 25
    draw.text((20, y), "Time: 14:32", fill='black', font=font)
    draw.text((300, y), "Cashier: John D.", fill='black', font=font)
    y += 30
    
    # Line separator
    draw.line([(20, y), (480, y)], fill='black', width=1)
    y += 25
    
    # Items header
    draw.text((20, y), "ITEM", fill='black', font=bold_font)
    draw.text((250, y), "QTY", fill='black', font=bold_font)
    draw.text((350, y), "PRICE", fill='black', font=bold_font)
    draw.text((420, y), "TOTAL", fill='black', font=bold_font)
    y += 25
    
    # Items
    items = [
        ("Wireless Mouse", 2, 29.99),
        ("USB-C Cable 6ft", 3, 12.99),
        ("Laptop Stand", 1, 49.99),
        ("Screen Cleaner", 2, 8.99),
    ]
    
    for item, qty, price in items:
        total = qty * price
        draw.text((20, y), item, fill='black', font=font)
        draw.text((250, y), str(qty), fill='black', font=font)
        draw.text((350, y), f"${price:.2f}", fill='black', font=font)
        draw.text((420, y), f"${total:.2f}", fill='black', font=font)
        y += 25
    
    # Line separator
    draw.line([(20, y), (480, y)], fill='black', width=1)
    y += 25
    
    # Subtotal and tax
    subtotal = sum(qty * price for _, qty, price in items)
    tax = subtotal * 0.0875
    total = subtotal + tax
    
    draw.text((20, y), "Subtotal:", fill='black', font=font)
    draw.text((420, y), f"${subtotal:.2f}", fill='black', font=font)
    y += 25
    
    draw.text((20, y), "Tax (8.75%):", fill='black', font=font)
    draw.text((420, y), f"${tax:.2f}", fill='black', font=font)
    y += 30
    
    # Total
    draw.line([(20, y), (480, y)], fill='black', width=2)
    y += 25
    draw.text((20, y), "TOTAL:", fill='black', font=bold_font)
    draw.text((420, y), f"${total:.2f}", fill='black', font=bold_font)
    y += 40
    
    # Footer
    draw.text((120, y), "Thank you for your purchase!", fill='black', font=font)
    y += 20
    draw.text((140, y), "Return policy: 30 days with receipt", fill='black', font=small_font)
    
    img.save('test_images/receipt.png')
    print("Created receipt.png")

if __name__ == "__main__":
    create_error_screenshot()
    create_sales_chart()
    create_receipt()
    print("\nAll test images created successfully!")
