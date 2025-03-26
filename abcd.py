from pypdl import Pypdl

dl = Pypdl()
dl.start(url="https://ir.iff.com/static-files/37376c57-3211-4253-9567-00da50dc4767", retries=2, file_path=f'downloads/{'asa'}', clear_terminal=False, overwrite=True)