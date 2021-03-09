"""Tests of imports of submodules and other dependencies"""
"""From github/scidash/sciunit"""

def import_all_modules(package, skip: list=None, verbose: bool=False,
                        prefix: str="", depth: int=0) -> None:
    """Recursively imports all subpackages, modules, and submodules of a
    given package.
    'package' should be an imported package, not a string.
    'skip' is a list of modules or subpackages not to import.
    Args:
        package ([type]): [description]
        skip (list, optional): [description]. Defaults to None.
        verbose (bool, optional): [description]. Defaults to False.
        prefix (str, optional): [description]. Defaults to "".
        depth (int, optional): [description]. Defaults to 0.
    """


    skip = [] if skip is None else skip

    for ff, modname, ispkg in pkgutil.walk_packages(path=package.__path__,
                                                    prefix=prefix,
                                                    onerror=lambda x: None):
        if ff.path not in package.__path__[0]:  # Solves weird bug
            continue
        if verbose:
            print('\t'*depth, modname)
        if modname in skip:
            if verbose:
                print('\t'*depth, '*Skipping*')
            continue
        module = '%s.%s' % (package.__name__, modname)
        subpackage = importlib.import_module(module)
        if ispkg:
            import_all_modules(subpackage, skip=skip,
                               verbose=verbose, depth=depth+1)


class ImportTestCase(unittest.TestCase):
    """Testing imports of modules and packages"""

    def test_import_everything(self):
        import readability
        # Recursively import all submodules
        import_all_modules(readability, verbose=True)


if __name__ == "__main__":
    unittest.main()
