# Template Images for Symbol Detection

This directory contains template images used for symbol detection in the P&ID analyzer.

## Currently Supported Symbols

The MVP focuses specifically on these ISA-5.1 standard symbols:

1. **pump.png** - Centrifugal pump template
2. **valve_manual.png** - Manual valve template
3. **valve_control.png** - Control valve template
4. **instrument_bubble.png** - Instrument bubble template
5. **tank.png** - Tank/vessel template

## How to Update Templates

To improve symbol detection accuracy, you may want to replace these templates with cropped symbols from your own P&ID diagrams:

1. Crop a clear, representative instance of each symbol from your diagrams
2. Save as PNG with transparent background if possible
3. Replace the corresponding file in this directory
4. Keep the same filename for each symbol type

## Adding New Symbol Types

The current MVP only supports the 5 symbols listed above. If you want to add support for additional symbols:

1. Add a new template PNG file in this directory
2. Update the `SUPPORTED_SYMBOLS` list in `backend/services/symbols.py`
3. Modify the symbol detection logic as needed

## Resources for ISA-5.1 Symbols

For reference or to obtain additional symbols, you can check these resources:

- ISA-5.1 standard documentation
- Online symbol libraries with proper licensing
- Open educational resources for P&ID symbols
