# Example Invalid TCL File
# This file contains intentional syntax errors for testing

# Missing closing brace
proc broken_proc {arg} {
set value $arg
puts "Processing: $value"
# Missing closing brace here

# Unmatched opening brace
if {$value > 10} {
puts "Value is large"
{
puts "Extra opening brace"
}

# Missing opening brace
set counter 0
while $counter < 5} {
puts "Counter: $counter"
incr counter
}

# Unmatched quote
set message "This string is missing a closing quote
puts $message

# Extra closing brace
proc another_proc {x y} {
set sum [expr {$x + $y}]
return $sum
}
}

# Nested braces with mismatch
set data {
{item1 value1}
{item2 value2
{item3 value3}
}

# Multiple errors in one block
foreach item {list1 list2 list3} {
if {[string length $item] > 5} {
puts "Long: $item
}
# Missing closing brace for if
# Missing closing brace for foreach

# Unmatched quote in command
set text "Start of string
puts $text
set more "Another string"

# Extra opening brace
{
set orphan "This has an extra opening brace"

# Missing closing brace in nested structure
namespace eval TestSpace {
variable count 0
proc increment {} {
variable count
incr count
# Missing closing brace for proc
# Missing closing brace for namespace

# Quote mismatch in array
array set config {
key1 "value1"
key2 "value2
key3 "value3"
}

# Final unmatched brace
set final {incomplete
