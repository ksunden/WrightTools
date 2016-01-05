'''
a collection of small, general purpose objects and methods
'''


### import ####################################################################


import os
import re
import ast
import copy
import collections
from time import clock

import numpy as np

import units


### file processing ###########################################################


def filename_parse(fstr):
    """
    parses a filepath string into it's path, name, and suffix
    """
    split = fstr.split('\\')
    if len(split) == 1:
        file_path = None
    else:
        file_path = '\\'.join(split[0:-1])
    split2 = split[-1].split('.')
    # try and guess whether a suffix is there or not
    # my current guess is based on the length of the final split string
    # suffix is either 3 or 4 characters
    if len(split2[-1]) in [3, 4, 5]:
        file_name = '.'.join(split2[0:-1])
        file_suffix = split2[-1]
    else:
        file_name = split[-1]
        file_suffix = None
    return file_path, file_name, file_suffix


def find_name(fname, suffix):
    """
    save the file using fname, and tacking on a number if fname already exists
    iterates until a unique name is found
    returns False if the loop malfunctions
    """
    good_name=False
    # find a name that isn't used by enumerating
    i = 1
    while not good_name:
        try:
            with open(fname+'.'+suffix):
               # file does exist
               # see if a number has already been guessed
               if fname.endswith(' ({0})'.format(i-1)):
                   # cut the old off before putting the new in
                   fname = fname[:-len(' ({0})'.format(i-1))]
               fname += ' ({0})'.format(i)
               i = i + 1
               # prevent infinite loop if the code isn't perfect
               if i > 100:
                   print 'didn\'t find a good name; index used up to 100!'
                   fname = False
                   good_name=True
        except IOError:
            # file doesn't exist and is safe to write to this path
            good_name = True
    return


def get_box_path():
    box_path = os.path.join(os.path.expanduser('~'), 'Box Sync', 'Wright Shared')
    
    if not os.path.isdir(box_path):
        #find root box directory given the current directory (given that current is within box)
        folders = os.getcwd().split('\\')
        found = False
        i=0
        while (found == False and i < range(len(folders))):
            if folders[i] == 'Box Sync':
                found = True
            i+=1
        if found:
            box_path =  str(os.path.join(folders[0], r'\\', *folders[1:i]))
            box_path = os.path.join(box_path, 'Wright Shared')
        else:
            print 'could not find the root directory'
            return None    
    
    return box_path


def get_timestamp():

    import time

    return time.strftime('%Y.%m.%d %H_%M_%S')


def glob_handler(extension, folder=None, identifier=None):
    '''
    returns a list of all files matching specified inputs \n
    if no folder is specified, looks in chdir
    '''

    import glob

    filepaths = []

    if folder:
        # comment out [ and ]...
        folder = folder.replace('[', '?')
        folder = folder.replace(']', '*')
        folder = folder.replace('?', '[[]')
        folder = folder.replace('*', '[]]')
        glob_str = os.path.join(folder, '*' + extension)
    else:
        glob_str = '*' + extension + '*'

    for filepath in glob.glob(glob_str):
        if identifier:
            if identifier in filepath:
                filepaths.append(filepath)
        else:
            filepaths.append(filepath)

    return filepaths


def plot_dats(folder=None, transpose=True):
    '''
    Convinience function to plot raw data from COLORS
    '''

    import data
    import artists

    if folder:
        pass
    else:
        folder = os.getcwd()

    files = glob_handler('.dat', folder = folder)

    for _file in files:

        print ' '

        try:

            dat_data = data.from_COLORS(_file)

            fname = filename_parse(_file)[1]

            dat_data.convert('wn')

            #1D
            if len(dat_data.axes) == 1:
                artist = artists.mpl_1D(dat_data, dat_data.axes[0].name)
                artist.plot(0, autosave = True, output_folder = folder, fname = fname)

            #2D
            elif len(dat_data.axes) == 2:
                if transpose: dat_data.transpose()
                artist = artists.mpl_2D(dat_data, dat_data.axes[0].name, dat_data.axes[1].name)
                artist.plot(0, pixelated = True, contours = 0, xbin = True, ybin = True,
                            autosave = True, output_folder = folder, fname = fname)

            else:
                print 'error! - dimensionality of data ({}) not recognized'.format(len(dat_data.axes))

        except:
            import sys
            print 'dat {} not recognized as plottible in plot_dats'.format(filename_parse(_file)[1])
            print sys.exc_info()[0]
            pass


def read_headers(filepath):
    '''
    Read 'Wright group formatted' headers from given path.
    
    Parameters
    ----------
    filepath : str
        Path of file.
        
    Returns
    -------
    OrderedDict
        Dictionary containing header information.
    '''
    headers = collections.OrderedDict()
    for line in open(filepath):
        if line[0] == '#':
            split = line.split(':')
            key = split[0][2:]
            item = split[1].split('\t')
            if split[1][0:3] == ' [[':  # case of multidimensional arrays
                arr = string2array(split[1][1:])
                headers[key] = arr
            else:
                if item[0] == '':
                    item = [item[1]]
                item = [i.strip() for i in item]  # remove dumb things
                item = [i if i is not '' else 'None' for i in item]  # handle empties
                # handle lists
                is_list = False
                list_chars = ['[', ']']
                for item_index, item_string in enumerate(item):
                    if item_string == '[]':
                        continue
                    for char in item_string:
                        if char in list_chars:
                            is_list = True
                    for char in list_chars:
                        item_string = item[item_index]
                        item[item_index] = item_string.replace(char, '')
                # eval contents
                item = [ast.literal_eval(i) for i in item]
                if len(item) == 1 and not is_list:
                    item = item[0]
                headers[key] = item
        else:
            break  # all header lines are at the beginning
    return headers


def write_headers(filepath, dictionary):
    '''
    Write 'Wright Group formatted' headers to given file. Headers written can
    be read again using read_headers.

    Paramters
    ---------
    filepath : str
        Path of file. File must not exist.
    dictionary : dict or OrderedDict
        Dictionary of header items.

    Returns
    -------
    str
        Filepath of file.
    '''
    dictionary = copy.deepcopy(dictionary)
    header_items = []
    for key, value in dictionary.items():
        header_item = key + ':'
        if type(value) == str:
            header_item += '\t' + '\'' + value + '\''
        elif type(value) == list:
            for i in range(len(value)):
                if type(value[i]) == str:
                    value[i] = '\'' + value[i] + '\''
                else:
                    value[i] = str(value[i])
            header_item += ' [' + '\t'.join(value) + ']'
        elif type(value).__module__ == np.__name__:  # anything from numpy
            if hasattr(value, 'shape'):
                string = array2string(value)
                header_item += ' ' + string
            else:
                header_item += ' [' + '\t'.join([str(i) for i in value]) + ']'
        else:
            header_item += '\t' + str(value)
        header_items.append(header_item)
    # write header
    header_str = ''
    for item in header_items:
        header_str += item + '\n'
    header_str = header_str[:-1]  # remove final newline charachter
    np.savetxt(filepath, [], header=header_str)
    # return
    return filepath


### math ######################################################################


def diff(xi, yi, order = 1):
    '''
    numpy.diff is a convinient method but it only works for evenly spaced data \n
    this method does the same but for an arbitrary 1D data slice \n
    returns numpy array [xi, yi_out]. edge points are padded.
    '''
    import numpy as np

    # grid data to be even ----------------------------------------------------

    # get function that describes data
    import scipy
    f = scipy.interpolate.interp1d(xi, yi, kind = 'linear')

    xi_even = np.linspace(min(xi), max(xi), len(xi))
    yi_even = f(xi_even)

    # call numpy.diff ---------------------------------------------------------

    yi_out_even = np.diff(yi_even, n = order)
    yi_out_even = np.pad(yi_out_even, order, mode = 'edge')
    yi_out_even = np.delete(yi_out_even, range(order))

    # put data back onto original xi points -----------------------------------

    xi_even += xi_even[1] - xi_even[0]  # offset by half step...

    fdiff = scipy.interpolate.interp1d(xi_even, yi_out_even,
                                       kind = 'linear', bounds_error = False)

    yi_out = fdiff(xi)

    return np.array([xi, yi_out])


def mono_resolution(grooves_per_mm, slit_width, focal_length, output_color, output_units='wn'):
    '''
    slit width mm, focal_length mm, output_color nm
    '''
    d_lambda = 1e6*slit_width/(grooves_per_mm*focal_length)  # nm
    upper = output_color + d_lambda/2  # nm
    lower = output_color - d_lambda/2  # nm
    return abs(units.converter(upper, 'nm', output_units) - 
               units.converter(lower, 'nm', output_units))


def smooth_1D(arr, n = 10):
    '''
    smooth 1D data by 'running average'\n
    int n smoothing factor (num points)
    '''
    for i in range(n, len(arr)-n):
        window = arr[i-n:i+n].copy()
        arr[i] = window.mean()
    return arr
    

def unique(arr, tolerance=1e-6):
    '''
    Return unique elements in 1D array, within tolerance.
    
    Parameters
    ----------
    arr : array_like
        Input array. This will be flattened if it is not already 1D.
    tolerance : number (optional)
        The tolerance for uniqueness.
        
    Returns
    -------
    array
        The sorted unique values.
    '''
    arr = list(arr.flatten())
    arr.sort()
    unique = []
    while len(arr) > 0:
        current = arr[0]
        lis = [xi for xi in arr if np.abs(current - xi) < tolerance]
        arr = [xi for xi in arr if not np.abs(lis[0] - xi) < tolerance]
        xi_lis_average = sum(lis) / len(lis)
        unique.append(xi_lis_average)
    return np.array(unique)


### uncategorized #############################################################


def array2string(array, sep='\t'):
    '''
    Generate a string from an array with useful formatting. Great for writing
    arrays into single lines in files.
    
    See Also
    --------
    string2array
    '''
    np.set_printoptions(threshold=array.size)
    string = np.array2string(array, separator=sep)
    string = string.replace('\n', sep)
    string = re.sub(r'({})(?=\1)'.format(sep), '', string)
    return string


def get_methods(the_class, class_only=False, instance_only=False,
                exclude_internal=True):
    '''
    get a list of strings corresponding to the names of the methods
    of an object.
    '''
    import inspect

    def acceptMethod(tup):
        # internal function that analyzes the tuples returned by getmembers
        # tup[1] is the actual member object
        is_method = inspect.ismethod(tup[1])
        if is_method:
            bound_to = tup[1].im_self
            internal = tup[1].im_func.func_name[:2] == '__' and tup[1].im_func.func_name[-2:] == '__'
            if internal and exclude_internal:
                include = False
            else:
                include = (bound_to == the_class and not instance_only) or (bound_to == None and not class_only)
        else:
            include = False
        return include

    # filter to return results according to internal function and arguments
    tups = filter(acceptMethod, inspect.getmembers(the_class))
    return [tup[0] for tup in tups]
    

def intersperse(lst, item):
    '''
    Put item between each existing item in list. \n
    From http://stackoverflow.com/a/5921708
    '''
    result = [item] * (len(lst) * 2 - 1)
    result[0::2] = lst
    return result


identity_operators = ['=', '+', '-', '*', '/', 'F']
def parse_identity(string):
    '''
    Parse an identity string into its components.
    
    Returns
    -------
    tuple of lists
        (names, operators)
    '''
    names = re.split("[=F]+", string)
    operators = [c for c in list(string) if c in identity_operators]
    return names, operators


class suppress_stdout_stderr(object):
    '''
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.

    This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).

    from http://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions

    with wt.kit.suppress_stdout_stderr():
        rogue_function()
    '''
    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])
        

def string2array(string, sep='\t'):
    '''
    Generate an array from a string created using array2string.
    
    See Also
    --------
    array2string
    '''
    # discover size
    size = string.count('\t')+1 
    # discover dimensionality
    dimensionality = 0
    while string[dimensionality] == '[':
        dimensionality += 1
    # discover shape
    shape = []       
    for i in range(1, dimensionality+1)[::-1]:
        to_match = '['*(i-1) + ' '
        count = string.count(to_match)
        shape.append(count)
    shape[-1] = size / shape[-2]
    for i in range(1, dimensionality-1)[::-1]:
        shape[i] = shape[i] / shape[i-1]
    shape = tuple(shape)
    # import list of floats
    l = string.split(' ')
    for i, item in enumerate(l):
        bad_chars = ['[', ']', '\t']
        for bad_char in bad_chars:
            item = item.replace(bad_char, '')
        l[i] = item
    for i in range(len(l))[::-1]:
        if l[i] == '':
            l.pop(i)
        else:
            l[i] = float(l[i])
    # create and reshape array
    arr = np.array(l)
    arr.shape = shape
    # finish
    return arr


unicode_dictionary = collections.OrderedDict()
unicode_dictionary['Alpha'] = u'\u0391'
unicode_dictionary['Beta'] = u'\u0392'
unicode_dictionary['Gamma'] = u'\u0392'
unicode_dictionary['Delta'] = u'\u0394'
unicode_dictionary['Epsilon'] = u'\u0395'
unicode_dictionary['Zeta'] = u'\u0396'
unicode_dictionary['Eta'] = u'\u0397'
unicode_dictionary['Theta'] = u'\u0398'
unicode_dictionary['Iota'] = u'\u0399'
unicode_dictionary['Kappa'] = u'\u039A'
unicode_dictionary['Lamda'] = u'\u039B'
unicode_dictionary['Mu'] = u'\u039C'
unicode_dictionary['Nu'] = u'\u039D'
unicode_dictionary['Xi'] = u'\u039E'
unicode_dictionary['Omicron'] = u'\u039F'
unicode_dictionary['Pi'] = u'\u03A0'
unicode_dictionary['Rho'] = u'\u03A1'
unicode_dictionary['Sigma'] = u'\u03A3'
unicode_dictionary['Tau'] = u'\u03A4'
unicode_dictionary['Upsilon'] = u'\u03A5'
unicode_dictionary['Phi'] = u'\u03A6'
unicode_dictionary['Chi'] = u'\u03A7'
unicode_dictionary['Psi'] = u'\u03A8'
unicode_dictionary['Omega'] = u'\u03A9'
unicode_dictionary['alpha'] = u'\u03B1'
unicode_dictionary['beta'] = u'\u03B2'
unicode_dictionary['gamma'] = u'\u03B3'
unicode_dictionary['delta'] = u'\u03B4'
unicode_dictionary['epsilon'] = u'\u03B5'
unicode_dictionary['zeta'] = u'\u03B6'
unicode_dictionary['eta'] = u'\u03B7'
unicode_dictionary['theta'] = u'\u03B8'
unicode_dictionary['iota'] = u'\u03B9'
unicode_dictionary['kappa'] = u'\u03BA'
unicode_dictionary['lamda'] = u'\u03BB'
unicode_dictionary['mu'] = u'\u03BC'
unicode_dictionary['nu'] = u'\u03BD'
unicode_dictionary['xi'] = u'\u03BE'
unicode_dictionary['omicron'] = u'\u03BF'
unicode_dictionary['pi'] = u'\u03C0'
unicode_dictionary['rho'] = u'\u03C1'
unicode_dictionary['sigma'] = u'\u03C3'
unicode_dictionary['tau'] = u'\u03C4'
unicode_dictionary['upsilon'] = u'\u03C5'
unicode_dictionary['phi'] = u'\u03C6'
unicode_dictionary['chi'] = u'\u03C7'
unicode_dictionary['psi'] = u'\u03C8'
unicode_dictionary['omega'] = u'\u03C9'


def update_progress(progress, carriage_return=True, length=50):
    '''
    prints a pretty progress bar to the console     \n
    accepts 'progress' as a percentage              \n
    bool carriage_return toggles overwrite behavior \n
    '''
    # make progress bar string
    progress_bar = ''
    num_oct = int(progress * (length/100.))
    progress_bar = progress_bar + '[{0}{1}]'.format('#'*num_oct, ' '*(length-num_oct))
    progress_bar = progress_bar + ' {}%'.format(np.round(progress, decimals = 2))
    if carriage_return:
        progress_bar = progress_bar + '\r'
        print progress_bar,
        return
    if progress == 100:
        progress_bar[-2:] = '\n'
    print progress_bar


class Timer:
    '''
    with Timer(): your_code()
    '''

    def __init__(self, verbose=True):
        self.verbose = verbose

    def __enter__(self, progress=None):
        self.start = clock()

    def __exit__(self, type, value, traceback):
        self.end = clock()
        self.interval = self.end - self.start
        if self.verbose:
            print 'elapsed time: {0} sec'.format(self.interval)
