#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import xlrd
import csv
import chardet


def safeint(s):
    if not s:
        return s
    f = float(s)
    r = round(f)
    if f == r:
        return int(f)
    else:
        raise ValueError(f"Can't parse {s} as int without losing precision")


def represents_int(s):
    try:
        safeint(s)
        return True
    except (ValueError, TypeError):
        return False


def represents_float(s):
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def parse_xls(book, header_row=0, sheet_index=0, sheet_name=None, skip_rows=1):
    rows = []
    if sheet_name:
        sheet = book.sheet_by_name(sheet_name)
    else:
        sheet = book.sheet_by_index(sheet_index)
    ncols = sheet.ncols
    # if a header cell is empty, the name of the column (e.g. "A") is used instead
    headers = {c: str(sheet.cell_value(header_row, c) or xlrd.formula.colname(c)) for c in range(ncols)}
    for r in range(header_row + skip_rows, sheet.nrows):
        entry = {}
        for c, h in headers.items():
            if h.strip() in entry:
                h = f"{h.strip()}{str(c)}"
            cell_type = sheet.cell_type(r, c)
            value = sheet.cell_value(r, c)
            if cell_type == xlrd.XL_CELL_DATE:
                entry[h] = xlrd.xldate.xldate_as_datetime(value, book.datemode)
            elif cell_type == xlrd.XL_CELL_EMPTY:
                entry[h] = None
            elif represents_int(value):
                entry[h] = int(value)
            elif represents_float(value):
                entry[h] = float(value)
            else:
                entry[h] = value

        rows.append(entry)
    return rows


def rows_from_xls(filename, header_row=0, sheet_index=0, sheet_name=None, skip_rows=1):
    xls = xlrd.open_workbook(filename)
    rows = parse_xls(xls, header_row, sheet_index, sheet_name, skip_rows)
    return rows


def rows_from_csv(input_file, delimiter=';', input_encoding='detect'):
    if input_encoding == 'detect':
        input_encoding = _detect_file_encoding(input_file)

    with open(input_file, 'r', encoding=input_encoding) as f:
        # if a list of delimiters is given, try to sniff the correct one
        if isinstance(delimiter, list):
            dialect = csv.Sniffer().sniff(f.read(), delimiter)
            f.seek(0)
            reader = csv.DictReader(f, dialect=dialect)
        else:
            reader = csv.DictReader(f, delimiter=delimiter)
        rows = [r for r in reader]
    return rows


def _detect_file_encoding(input_file, line_count=20):
    with open(input_file, 'rb') as f:
        # read some lines
         rawdata = b''.join([f.readline() for _ in range(line_count)])
    return chardet.detect(rawdata)['encoding']


def write_csv(rows, out=None, skip_header=False):
    header = rows[0].keys()
    outfile = open(out, 'w', newline='') if out else sys.stdout

    writer = csv.DictWriter(
        outfile,
        header,
        delimiter=',',
        quotechar='"',
        lineterminator='\n',
        quoting=csv.QUOTE_MINIMAL
    )
    if not skip_header:
        writer.writeheader()
    writer.writerows(rows)

    if outfile is not sys.stdout:
       outfile.close()
