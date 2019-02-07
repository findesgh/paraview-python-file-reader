"""
Example python file reader demonstrating some of the features available for
python programmable file readers.

This file does not actually provide any output, but is just here to show the
options available when using python_filter_generator.

Daan van Vugt <daanvanvugt@gmail.com>
"""
Name = 'FbinFileReader'
Label = 'Read a file in ParaView using python'
Help = 'Example file reader using a Python Programmable Filter to act as a vtk source'
Extension = 'in'
FileDescription = 'Numpy arrays'

from collections import OrderedDict

NumberOfInputs = 0
OutputDataType = 'vtkImageData'

# Create a new class to distinguish the list to select
# Keys = string names
# Values = 1 or 0 (enabled by default or not)
class ArraySelectionDomain(OrderedDict):
    pass
class PropertyGroup(OrderedDict):
    pass

# These properties are put in a panel where you can tune the properties of your
# source. The first element of each tuple is the name of the variable available
# in your python script, the second is the default value.

# Top-level tuples are propertygroups. One level below is a list of
# dictionaries for the elements

# Names are converted to labels by '_' > ' ' and uppercasing the first letter
Properties = OrderedDict([
    # Which variables to read from the file
    ('variables', ArraySelectionDomain([
        ('x', 1)
    ])),
    ('PythonPath', '/opt/crashToVTK')
])


def RequestData(self):
    """
    Create a VTK output given the list of filenames and the current timestep.
    This script can access self and FileNames and should return an output of
    type OutputDataType above
    """
    # from paraview import vtk is done automatically in the reader
    import crashToVTK.crashToVTK as crashToVTK


    def GetUpdateTimestep(algorithm):
        """
        Returns the requested time value, or None if not present
        """
        executive = algorithm.GetExecutive()
        outInfo = executive.GetOutputInformation(0)
        return outInfo.Get(executive.UPDATE_TIME_STEP()) \
                if outInfo.Has(executive.UPDATE_TIME_STEP()) else None
    # Get the current timestep
    req_time = GetUpdateTimestep(self)

    if req_time is None:
        req_time = 0

    # output variable
    output = self.GetImageDataOutput()
    # output = self.GetUniformGridOutput()

    extent = crashToVTK.getStructuredGrid(FileNames[0], output)
    return output


def RequestInformation(self):
    """
    Given a list of filenames this script should output how many timesteps are
    available.

    See paraview guide 13.2.2
    """
    from paraview import util

    op = self.GetOutput()
    # ex = [x for x in op.GetExtent()]
    print [x for x in op.GetExtent()]
    ex = [0, 128, 0, 128, 0, 128]

    # this here seems to be necessary, for some reason. Otherwise paraview is
    # not happy:
    # https://stackoverflow.com/questions/42858026/how-to-write-a-porgrammablesource-filter-to-display-a-numpy-array-as-a-vtkimaged
    # something similar is also mentioned here:
    # https://vtk.org/Wiki/VTK/Examples/Python/vtkWithNumpy
    util.SetOutputWholeExtent(self, ex)

    def setOutputTimesteps(algorithm):
        executive = algorithm.GetExecutive()
        outInfo = executive.GetOutputInformation(0)

        # Calculate list of timesteps here
        xtime = [j for j, file in enumerate(FileNames)]

        outInfo.Remove(executive.TIME_STEPS())
        for i in range(len(FileNames)):
            outInfo.Append(executive.TIME_STEPS(), xtime[i])

        # Remove and set time range info
        outInfo.Remove(executive.TIME_RANGE())
        outInfo.Append(executive.TIME_RANGE(), xtime[0])
        outInfo.Append(executive.TIME_RANGE(), xtime[-1])

    setOutputTimesteps(self)
