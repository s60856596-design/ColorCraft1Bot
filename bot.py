import os
import sys
import logging
import random
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from PIL import Image, ImageDraw

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
def get_token():
    token = os.environ.get('BOT_TOKEN')
    if not token:
        token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("❌ No BOT_TOKEN found in environment variables!")
        logger.error("Please add BOT_TOKEN to your Railway Variables.")
        sys.exit(1)
    return token

TOKEN = get_token()
logger.info("✅ Bot token loaded successfully!")

# Color utility functions
def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    """Convert RGB to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"

def generate_random_color():
    """Generate a random hex color."""
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return rgb_to_hex(r, g, b)

def generate_palette(color_count=5):
    """Generate a random color palette."""
    palette = []
    for _ in range(color_count):
        palette.append(generate_random_color())
    return palette

def generate_complementary(hex_color):
    """Generate complementary color."""
    r, g, b = hex_to_rgb(hex_color)
    comp_r = 255 - r
    comp_g = 255 - g
    comp_b = 255 - b
    return rgb_to_hex(comp_r, comp_g, comp_b)

def generate_analogous(hex_color):
    """Generate analogous colors (shift hue by ±30 degrees)."""
    # Simplified version - for demonstration
    r, g, b = hex_to_rgb(hex_color)
    # Create variations by adjusting RGB values
    colors = []
    # Original
    colors.append(hex_color)
    # Shift towards red
    colors.append(rgb_to_hex(min(255, r + 50), max(0, g - 30), max(0, b - 30)))
    # Shift towards blue
    colors.append(rgb_to_hex(max(0, r - 30), max(0, g - 30), min(255, b + 50)))
    return colors

def generate_triadic(hex_color):
    """Generate triadic colors (120° apart on color wheel)."""
    r, g, b = hex_to_rgb(hex_color)
    # Simplified triadic - rotate RGB values
    colors = []
    colors.append(hex_color)  # Original
    colors.append(rgb_to_hex(g, b, r))  # Rotate
    colors.append(rgb_to_hex(b, r, g))  # Rotate again
    return colors

def generate_monochromatic(hex_color, count=5):
    """Generate monochromatic palette with different shades."""
    r, g, b = hex_to_rgb(hex_color)
    palette = []
    for i in range(count):
        factor = 0.2 + (i * 0.15)  # Creates different brightness levels
        new_r = min(255, int(r * factor))
        new_g = min(255, int(g * factor))
        new_b = min(255, int(b * factor))
        palette.append(rgb_to_hex(new_r, new_g, new_b))
    return palette

def create_color_image(hex_colors, width=600, height=150):
    """Create an image showing color swatches."""
    img = Image.new('RGB', (width, height), '#ffffff')
    draw = ImageDraw.Draw(img)
    
    swatch_width = width // len(hex_colors)
    swatch_height = height
    
    for i, hex_color in enumerate(hex_colors):
        x = i * swatch_width
        draw.rectangle([x, 0, x + swatch_width, swatch_height], fill=hex_color)
        
        # Add border
        draw.rectangle([x, 0, x + swatch_width, swatch_height], outline='#333333', width=1)
    
    # Add hex labels at bottom
    for i, hex_color in enumerate(hex_colors):
        x = i * swatch_width + 5
        y = height - 20
        draw.text((x, y), hex_color, fill='#ffffff' if is_dark(hex_color) else '#000000')
    
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return img_buffer

def is_dark(hex_color):
    """Check if a color is dark (for text contrast)."""
    r, g, b = hex_to_rgb(hex_color)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return brightness < 128

def create_palette_preview(palette):
    """Create a text preview of the palette with color codes."""
    preview = "🎨 **Color Palette:**\n\n"
    for i, color in enumerate(palette, 1):
        preview += f"{i}. `{color}`  "
        # Add color indicator using emoji (approximate)
        if i % 3 == 0:
            preview += "\n"
    return preview

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message with quick action buttons."""
    user = update.effective_user
    
    keyboard = [
        [
            InlineKeyboardButton("🎨 Random Palette", callback_data="palette_5"),
            InlineKeyboardButton("🎯 3 Colors", callback_data="palette_3"),
        ],
        [
            InlineKeyboardButton("🌈 7 Colors", callback_data="palette_7"),
            InlineKeyboardButton("🔮 10 Colors", callback_data="palette_10"),
        ],
        [
            InlineKeyboardButton("🔄 Complementary", callback_data="complementary_random"),
            InlineKeyboardButton("📐 Triadic", callback_data="triadic_random"),
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
🎨 **Welcome to ColorCraft1Bot, {user.first_name}!**

I help you generate and explore beautiful color palettes!

**Commands:**
/start - Show this menu
/palette [count] - Generate random palette (2-10)
/complementary [hex] - Get complementary colors
/triadic [hex] - Get triadic colors
/analogous [hex] - Get analogous colors
/monochromatic [hex] - Get monochromatic palette
/help - Show all commands

**Examples:**
`/palette 5`
`/complementary #FF5733`
`/triadic #2196F3`

Click a button below to get started!
"""
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message."""
    help_text = """
🎨 **ColorCraft1Bot Help**

**Commands:**
/palette [count] - Generate random palette (2-10 colors)
/complementary [hex] - Get complementary colors
/triadic [hex] - Get triadic colors (3 colors 120° apart)
/analogous [hex] - Get analogous colors (similar hues)
/monochromatic [hex] - Get monochromatic palette

**Examples:**
`/palette` → 5 random colors
`/palette 3` → 3 random colors
`/complementary #FF5733` → Complementary colors
`/triadic #2196F3` → Triadic colors
`/monochromatic #FF5733` → Monochromatic palette

**What you get:**
• Visual color swatches
• HEX codes for each color
• Color harmony information

💡 **Tip:** Use the buttons for quick access!
"""
    await update.message.reply_text(help_text)

async def palette_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate and send a random palette."""
    args = context.args
    count = 5
    if args and args[0].isdigit():
        count = max(2, min(10, int(args[0])))
    
    palette = generate_palette(count)
    img_buffer = create_color_image(palette)
    
    response = create_palette_preview(palette)
    response += f"\n📊 **Count:** {len(palette)} colors"
    
    await update.message.reply_photo(
        photo=img_buffer,
        caption=response
    )

async def complementary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate complementary colors."""
    args = context.args
    hex_color = args[0] if args else None
    
    if not hex_color:
        # Generate random color
        hex_color = generate_random_color()
        await update.message.reply_text(f"🎨 No color provided. Using random: `{hex_color}`")
    
    if not hex_color.startswith('#') or len(hex_color) != 7:
        await update.message.reply_text(
            "❌ Invalid hex color format!\n"
            "Please use format: `#RRGGBB`\n"
            "Example: `/complementary #FF5733`"
        )
        return
    
    try:
        comp_color = generate_complementary(hex_color)
        palette = [hex_color, comp_color]
        img_buffer = create_color_image(palette)
        
        response = f"🎨 **Complementary Colors:**\n\n"
        response += f"Primary: `{hex_color}`\n"
        response += f"Complement: `{comp_color}`\n\n"
        response += "💡 Complementary colors are opposite on the color wheel.\n"
        response += "They create high contrast and vibrant designs."
        
        await update.message.reply_photo(
            photo=img_buffer,
            caption=response
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def triadic_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate triadic colors."""
    args = context.args
    hex_color = args[0] if args else None
    
    if not hex_color:
        hex_color = generate_random_color()
        await update.message.reply_text(f"🎨 No color provided. Using random: `{hex_color}`")
    
    if not hex_color.startswith('#') or len(hex_color) != 7:
        await update.message.reply_text(
            "❌ Invalid hex color format!\n"
            "Please use format: `#RRGGBB`\n"
            "Example: `/triadic #2196F3`"
        )
        return
    
    try:
        palette = generate_triadic(hex_color)
        img_buffer = create_color_image(palette)
        
        response = f"🎨 **Triadic Colors:**\n\n"
        for i, color in enumerate(palette, 1):
            response += f"{i}. `{color}`\n"
        response += "\n💡 Triadic colors are evenly spaced (120°) on the color wheel.\n"
        response += "They create balanced and colorful designs."
        
        await update.message.reply_photo(
            photo=img_buffer,
            caption=response
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def analogous_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate analogous colors."""
    args = context.args
    hex_color = args[0] if args else None
    
    if not hex_color:
        hex_color = generate_random_color()
        await update.message.reply_text(f"🎨 No color provided. Using random: `{hex_color}`")
    
    if not hex_color.startswith('#') or len(hex_color) != 7:
        await update.message.reply_text(
            "❌ Invalid hex color format!\n"
            "Please use format: `#RRGGBB`\n"
            "Example: `/analogous #FF5733`"
        )
        return
    
    try:
        palette = generate_analogous(hex_color)
        img_buffer = create_color_image(palette)
        
        response = f"🎨 **Analogous Colors:**\n\n"
        for i, color in enumerate(palette, 1):
            response += f"{i}. `{color}`\n"
        response += "\n💡 Analogous colors are adjacent on the color wheel.\n"
        response += "They create harmonious and pleasing designs."
        
        await update.message.reply_photo(
            photo=img_buffer,
            caption=response
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def monochromatic_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate monochromatic palette."""
    args = context.args
    hex_color = args[0] if args else None
    
    if not hex_color:
        hex_color = generate_random_color()
        await update.message.reply_text(f"🎨 No color provided. Using random: `{hex_color}`")
    
    if not hex_color.startswith('#') or len(hex_color) != 7:
        await update.message.reply_text(
            "❌ Invalid hex color format!\n"
            "Please use format: `#RRGGBB`\n"
            "Example: `/monochromatic #FF5733`"
        )
        return
    
    try:
        palette = generate_monochromatic(hex_color, 5)
        img_buffer = create_color_image(palette)
        
        response = f"🎨 **Monochromatic Palette:**\n\n"
        for i, color in enumerate(palette, 1):
            response += f"{i}. `{color}`\n"
        response += "\n💡 Monochromatic palettes use different shades of one color.\n"
        response += "They create cohesive and professional designs."
        
        await update.message.reply_photo(
            photo=img_buffer,
            caption=response
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "help":
        await query.edit_message_text(
            "🎨 **ColorCraft1Bot Help**\n\n"
            "**Commands:**\n"
            "/palette [count] - Generate random palette\n"
            "/complementary [hex] - Complementary colors\n"
            "/triadic [hex] - Triadic colors\n"
            "/analogous [hex] - Analogous colors\n"
            "/monochromatic [hex] - Monochromatic palette\n\n"
            "Click /start to return to main menu."
        )
        return
    
    if data.startswith("palette_"):
        count = int(data.replace("palette_", ""))
        palette = generate_palette(count)
        img_buffer = create_color_image(palette)
        response = create_palette_preview(palette)
        response += f"\n📊 **Count:** {len(palette)} colors"
        
        await query.message.reply_photo(
            photo=img_buffer,
            caption=response
        )
        await query.delete_message()
        return
    
    if data == "complementary_random":
        hex_color = generate_random_color()
        comp_color = generate_complementary(hex_color)
        palette = [hex_color, comp_color]
        img_buffer = create_color_image(palette)
        
        response = f"🎨 **Complementary Colors:**\n\n"
        response += f"Primary: `{hex_color}`\n"
        response += f"Complement: `{comp_color}`\n\n"
        response += "💡 Complementary colors create high contrast and vibrant designs."
        
        await query.message.reply_photo(
            photo=img_buffer,
            caption=response
        )
        await query.delete_message()
        return
    
    if data == "triadic_random":
        hex_color = generate_random_color()
        palette = generate_triadic(hex_color)
        img_buffer = create_color_image(palette)
        
        response = f"🎨 **Triadic Colors:**\n\n"
        for i, color in enumerate(palette, 1):
            response += f"{i}. `{color}`\n"
        response += "\n💡 Triadic colors create balanced and colorful designs."
        
        await query.message.reply_photo(
            photo=img_buffer,
            caption=response
        )
        await query.delete_message()
        return

def main() -> None:
    """Start the bot."""
    try:
        # Create Application
        application = Application.builder().token(TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("palette", palette_command))
        application.add_handler(CommandHandler("complementary", complementary_command))
        application.add_handler(CommandHandler("triadic", triadic_command))
        application.add_handler(CommandHandler("analogous", analogous_command))
        application.add_handler(CommandHandler("monochromatic", monochromatic_command))
        
        # Add callback handler for inline buttons
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Start the Bot
        logger.info("🚀 ColorCraft1Bot started successfully!")
        logger.info("🎨 Press Ctrl+C to stop.")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
