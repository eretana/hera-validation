"""
Prepare reference files for absolute calibration.
"""
import numpy as np
from astropy import units
from pyuvdata import UVData

from . import sim_prep

a = sim_prep.abscal_model_argparser()

# Load the simulation file and the reference file.
if a.verbose:
    print("Reading files...")
sim_uvd = UVData()
sim_uvd.read(a.simfile)
ref_uvd = UVData()
ref_uvd.read(a.reffile, read_data=False)

# Do a downselection in time on the simulation.
if a.verbose:
    print("Performing time downselect...")
lst_min = a.lst_min * units.hr.to('day') * 2 * np.pi
lst_max = a.lst_max * units.hr.to('day') * 2 * np.pi
sim_times = np.unique(sim_uvd.time_array)
sim_lsts = np.unique(sim_uvd.lst_array)
keep_times = sim_times[np.logical_and(lst_min < sim_lsts, sim_lsts < lst_max)]
sim_uvd.select(times=keep_times)

# Now inflate the simulation and adjust the array.
if a.verbose:
    print("Inflating by redundancy...")
sim_uvd.inflate_by_redundancy()
if a.verbose:
    print("Choosing which antennas to keep...")
sim_uvd = sim_prep.downselect_antennas(sim_uvd, ref_uvd)

# Now chunk the sim and save it.
if a.verbose:
    print("Chunking files and writing to disk...")
sim_prep.chunk_sim_and_save(
    sim_uvd, 
    a.savedir, 
    Nint_per_file=a.Nint_per_file, 
    sky_cmp='abscal',
    state='model',
    clobber=a.clobber
)