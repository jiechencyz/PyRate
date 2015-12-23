"""
This is a python implementation of the refphsest.m of pirate.
"""
__author__ = 'Sudipta Basak'
__date_created__ = '22/12/15'

import numpy as np
from pyrate import config as cf


def estimate_ref_phase(ifgs, params, refpx, refpy):
    number_ifgs = len(ifgs)
    ref_phs = np.zeros(number_ifgs)

    # set reference phase as the average of the whole image (recommended)
    if int(params[cf.REF_EST_METHOD]) == 1:
        ifg_phase_data_sum = np.zeros(ifgs[0].shape, dtype=np.float64)
        for i in ifgs:
            ifg_phase_data_sum += i.phase_data
        comp = np.isnan(ifg_phase_data_sum)  # this is the same as in Matlab
        comp = np.ravel(comp, order='F')  # this is the same as in Matlab
        print comp[:50]
        for n, i in enumerate(ifgs):
            ifgv = np.ravel(i.phase_data, order='F')
            ifgv[comp == 1] = np.nan
            # reference phase
            ref_phs[n] = np.nanmedian(ifgv)
            i.phase_data -= ref_phs[n]
    else:
        raise NotImplementedError('This ref estimation method '
                                  'has not been implemetned. Use refest=1')

    return ref_phs, ifgs


if __name__ == "__main__":
    import os
    import shutil
    from subprocess import call

    from pyrate.scripts import run_pyrate
    from pyrate import matlab_mst_kruskal as matlab_mst
    from pyrate.tests.common import SYD_TEST_MATLAB_ORBITAL_DIR, SYD_TEST_OUT

    # start each full test run cleanly
    shutil.rmtree(SYD_TEST_OUT, ignore_errors=True)

    os.makedirs(SYD_TEST_OUT)

    params = cf.get_config_params(
            os.path.join(SYD_TEST_MATLAB_ORBITAL_DIR, 'orbital_error.conf'))

    call(["python", "pyrate/scripts/run_prepifg.py",
          os.path.join(SYD_TEST_MATLAB_ORBITAL_DIR, 'orbital_error.conf')])

    xlks, ylks, crop = run_pyrate.transform_params(params)

    base_ifg_paths = run_pyrate.original_ifg_paths(params[cf.IFG_FILE_LIST])

    dest_paths = run_pyrate.get_dest_paths(base_ifg_paths, crop, params, xlks)

    ifg_instance = matlab_mst.IfgListPyRate(datafiles=dest_paths)

    ifgs = ifg_instance.ifgs
    for i in ifgs:
        i.convert_to_mm()
        i.write_modified_phase()

    refx, refy = run_pyrate.find_reference_pixel(ifgs, params)

    if params[cf.ORBITAL_FIT] != 0:
        run_pyrate.remove_orbital_error(ifgs, params)



    ref_phs, ifgs = estimate_ref_phase(ifgs, params, refx, refy)
    print ref_phs

