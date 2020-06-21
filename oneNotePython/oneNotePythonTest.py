from onepy import OneNote

if __name__ == '__main__':
    on = OneNote()
    print [nbk.name for nbk in on.hierarchy]
    for nbk in on.hierarchy:
        if nbk.name == "Investigations":
            print [str(sec) for sec in nbk]
            for sec in nbk:
                if str(sec) == "General":
                    print [str(page.name) for page in sec]

