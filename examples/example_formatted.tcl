# Example Formatted TCL File
# This demonstrates the expected output after formatting

# Simple variable assignments (with alignment enabled)
set name                     "John Doe"
set age                      30
set email                    "john.doe@example.com"

# Procedure definition with proper indentation
proc calculate_sum {a b} {
  set result [expr {$a + $b}]
  return $result
}

# Conditional statements with consistent indentation
if {$age >= 18} {
  puts "Adult"
} else {
  puts "Minor"
}

# Foreach loop with nested logic
foreach item {apple banana cherry date elderberry} {
  if {[string length $item] > 5} {
    puts "Long name: $item"
  } else {
    puts "Short name: $item"
  }
}

# While loop
set counter 0
while {$counter < 5} {
  puts "Counter: $counter"
  incr counter
}

# Switch statement
switch $name {
  "John Doe" {
    puts "Found John"
  }
  "Jane Smith" {
    puts "Found Jane"
  }
  default {
    puts "Unknown person"
  }
}

# Namespace definition
namespace eval MyNamespace {
  variable data "namespace data"
  proc helper {arg} {
    return [string toupper $arg]
  }
}

# Long list expanded to multiple lines (when expansion enabled)
set long_list {
  item1
  item2
  item3
  item4
  item5
  item6
  item7
  item8
  item9
  item10
  item11
  item12
}

# Set commands with alignment
set x                        10
set variable_name            20
set another_var              30
set very_long_variable_name  40

# Nested braces with proper indentation
set nested_data {
  {key1 value1}
  {key2 value2}
  {key3 value3}
}

# Command substitution (preserved)
set current_time [clock format [clock seconds]]
set file_list [glob *.tcl]

# String with quotes (preserved)
set message "This is a \"quoted\" string"

# Array operations
array set config {
  host    "localhost"
  port    8080
  timeout 30
}

# Multi-line command with continuation (preserved)
set long_command "This is a very long string that \
continues on the next line and \
demonstrates line continuation"

# Comments are preserved
# This is a comment
puts "Hello, World!"  ;# Inline comment

# Empty lines are handled appropriately

# Final statement
puts "TCL formatting example complete"
