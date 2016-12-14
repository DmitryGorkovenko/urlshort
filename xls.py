from xlutils.filter import process,XLRDReader,XLWTWriter


def copy(wb):
    w = XLWTWriter()
    process(XLRDReader(wb,'unknown.xls'), w)
    return w.output[0][1], w.style_list
