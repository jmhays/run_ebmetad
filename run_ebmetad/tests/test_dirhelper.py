from run_ebmetad.directory_helper import DirectoryHelper
import os


def test_directory(tmpdir):
    """
    Checks that directory creation for EBMetaD runs is functional.
    :param tmpdir: temporary pytest directory
    """
    my_home = os.path.abspath(os.getcwd())

    top_dir = tmpdir.mkdir("top_directory")
    dir_helper = DirectoryHelper(top_dir, 0)
    dir_helper.build_working_dir()
    dir_helper.change_dir('ensemble_num')
    assert (os.getcwd() == '{}/mem_0'.format(top_dir))

    os.chdir(my_home)
