#!/usr/bin/env ruby
# coding: utf-8

# Extract all text from a single PDF

# require 'rubygems'
require 'pdf/reader'

# dont forget to install the gem into local system using:   gem install pdf-reader
# require 'open-uri'

# first argument to script is asigned to file_name variable
file_name = ARGV[0]
reader = PDF::Reader.new(file_name) # file must exist in the same path as this script

content = ''

reader.pages.each do |page|
  page_text = page.text.strip!
  content += page_text
end
# puts content.encode("ISO-8859-1", invalid: :replace, undef: :replace)
File. open("#{file_name.split('.')[0]}.txt", "w:UTF-8") do |file|
  file.write content
end
