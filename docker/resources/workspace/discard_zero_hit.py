import argparse
import xml.etree.ElementTree as ET

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("src", type=str)
  parser.add_argument("dest", type=str)
  args = parser.parse_args()

  tree = ET.parse(args.src)
  root = tree.getroot()
  packages = root[1]
  for package in packages:
    for classes in package:
      for _class in classes:
        methods = _class.find('methods')
        for method in methods.findall('method'):
          lines = method.find('lines')
          for line in lines.findall('line'):
            hits = int(line.attrib['hits'])
            if hits == 0:
              lines.remove(line)
          remaining_lines = len(lines.findall('line'))
          if remaining_lines == 0:
            methods.remove(method)
        lines = _class.find('lines')
        _class.remove(lines)

  tree.write(args.dest)
