# TCL Formatter & Debugger - Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                          │
│                              (PyQt6 GUI)                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────┐    │
│  │                     TCLFormatterUI                            │    │
│  │                    (QMainWindow)                              │    │
│  │                                                               │    │
│  │  • File Selection Widget                                     │    │
│  │  • Formatting Options (Checkboxes)                           │    │
│  │  • Format Button                                             │    │
│  │  • Status Display (QTextEdit)                                │    │
│  └───────────────────┬───────────────────────────────────────────┘    │
│                      │                                                 │
│                      │ creates & manages                               │
│                      ▼                                                 │
│  ┌───────────────────────────────────────────────────────────────┐    │
│  │                  FormatterWorker                              │    │
│  │                   (QThread)                                   │    │
│  │                                                               │    │
│  │  • Runs formatting in background                             │    │
│  │  • Prevents UI freezing                                      │    │
│  │  • Emits results via signals                                 │    │
│  └───────────────────┬───────────────────────────────────────────┘    │
│                      │                                                 │
└──────────────────────┼─────────────────────────────────────────────────┘
                       │
                       │ invokes
                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         (Core Business Logic)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────┐    │
│  │                      TCLFormatter                             │    │
│  │                   (Main Orchestrator)                         │    │
│  │                                                               │    │
│  │  • format_file(path, options) → FormattingResult             │    │
│  │  • Coordinates all engines                                   │    │
│  │  • Handles file I/O with encoding detection                  │    │
│  │  • Generates output files or error logs                      │    │
│  └───────────────────┬───────────────────────────────────────────┘    │
│                      │                                                 │
│                      │ delegates to                                    │
│                      ▼                                                 │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                    SPECIALIZED ENGINES                           │ │
│  ├──────────────────────────────────────────────────────────────────┤ │
│  │                                                                  │ │
│  │  ┌────────────────────────────────────────────────────────┐    │ │
│  │  │         SyntaxValidator                                │    │ │
│  │  │                                                        │    │ │
│  │  │  • Stack-based brace/quote matching                   │    │ │
│  │  │  • Line-by-line error detection                       │    │ │
│  │  │  • Returns: List[SyntaxError]                         │    │ │
│  │  └────────────────────────────────────────────────────────┘    │ │
│  │                                                                  │ │
│  │  ┌────────────────────────────────────────────────────────┐    │ │
│  │  │         IndentationEngine                              │    │ │
│  │  │                                                        │    │ │
│  │  │  • Applies 2-space indentation                        │    │ │
│  │  │  • Tracks brace nesting levels                        │    │ │
│  │  │  • Handles block keywords (if, foreach, proc, etc.)   │    │ │
│  │  │  • Optional strict mode for continuations             │    │ │
│  │  └────────────────────────────────────────────────────────┘    │ │
│  │                                                                  │ │
│  │  ┌────────────────────────────────────────────────────────┐    │ │
│  │  │         ListExpansionEngine                            │    │ │
│  │  │                                                        │    │ │
│  │  │  • Detects lists > 80 characters                      │    │ │
│  │  │  • Expands to multiline format                        │    │ │
│  │  │  • Preserves nested structures                        │    │ │
│  │  └────────────────────────────────────────────────────────┘    │ │
│  │                                                                  │ │
│  │  ┌────────────────────────────────────────────────────────┐    │ │
│  │  │         AlignmentEngine                                │    │ │
│  │  │                                                        │    │ │
│  │  │  • Finds consecutive set command blocks               │    │ │
│  │  │  • Aligns assignment values                           │    │ │
│  │  │  • Calculates column positions                        │    │ │
│  │  └────────────────────────────────────────────────────────┘    │ │
│  │                                                                  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                       │
                       │ produces
                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           OUTPUT LAYER                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────┐      ┌──────────────────────────────┐    │
│  │   Success Path          │      │   Failure Path               │    │
│  ├─────────────────────────┤      ├──────────────────────────────┤    │
│  │                         │      │                              │    │
│  │  filename_formatted.tcl │      │  errors.log                  │    │
│  │                         │      │                              │    │
│  │  • Formatted TCL code   │      │  • Line-numbered errors      │    │
│  │  • Same directory as    │      │  • Detailed descriptions     │    │
│  │    input file           │      │  • Same directory as input   │    │
│  │  • Overwrites if exists │      │                              │    │
│  └─────────────────────────┘      └──────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. User selects .tcl file via GUI                                     │
│  2. User configures formatting options (checkboxes)                    │
│  3. User clicks "Format File" button                                   │
│  4. TCLFormatterUI creates FormatterWorker thread                      │
│  5. FormatterWorker invokes TCLFormatter.format_file()                 │
│  6. TCLFormatter reads file with encoding detection (chardet)          │
│  7. SyntaxValidator checks for errors                                  │
│     ├─ If errors found → Generate errors.log → Return failure         │
│     └─ If valid → Continue to formatting                              │
│  8. IndentationEngine applies consistent indentation                   │
│  9. (Optional) ListExpansionEngine expands long lists                  │
│ 10. (Optional) AlignmentEngine aligns set commands                     │
│ 11. TCLFormatter writes formatted output to *_formatted.tcl            │
│ 12. FormatterWorker emits finished signal with result                  │
│ 13. TCLFormatterUI displays success/error message in status area      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                        KEY DESIGN PATTERNS                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  • Separation of Concerns: UI, business logic, and engines separated   │
│  • Single Responsibility: Each engine handles one formatting aspect    │
│  • Threading: Background processing prevents UI blocking               │
│  • Signal/Slot: Qt signals for async communication                     │
│  • Dataclasses: Structured data (SyntaxError, FormattingResult, etc.)  │
│  • Stack-based Validation: Efficient brace/quote matching              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### UI Layer
- **TCLFormatterUI**: Main window, user interaction, file selection, option management
- **FormatterWorker**: Background thread execution, prevents UI freezing

### Engine Layer
- **TCLFormatter**: Orchestrates formatting pipeline, handles file I/O
- **SyntaxValidator**: Validates TCL syntax before formatting
- **IndentationEngine**: Applies consistent indentation rules
- **ListExpansionEngine**: Improves readability of long lists
- **AlignmentEngine**: Aligns set command assignments

### Output Layer
- **Formatted File**: Successfully formatted TCL code
- **Error Log**: Detailed syntax error report with line numbers
