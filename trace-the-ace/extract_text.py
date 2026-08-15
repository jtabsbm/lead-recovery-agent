#!/usr/bin/env python3
"""Extract text from saved competition HTML pages."""
import re, html, sys

def textify(path):
    c = open(path).read()
    t = re.sub(r'<script[^>]*>.*?</script>', ' ', c, flags=re.S)
    t = re.sub(r'<style[^>]*>.*?</style>', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n\s*\n+', '\n', t)
    return t

if __name__ == "__main__":
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    end = int(sys.argv[3]) if len(sys.argv) > 3 else 5000
    print(textify(sys.argv[1])[start:end])
