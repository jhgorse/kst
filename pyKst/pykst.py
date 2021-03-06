import sys
import math
import ctypes
import atexit
import os

try:
  from PySide import QtCore, QtNetwork, QtGui
except ImportError as err1:
  try:
    from PyQt4 import QtCore, QtNetwork, QtGui
  except ImportError as err2:
    print("ImportError: {} and {}. One of the two is required.".format(err1, err2))
    sys.exit()

QtGui.QApplication([""])

from numpy import *
import tempfile
import time
import subprocess

def cleanTmpFile(file):
	os.remove(file.name)

def b2str(val):
  if isinstance(val, bool):
    return "True" if val else "False"
  else:
    return str(val)


class Client:
  """ An interface to a running kst session. 

  A client provides a connection to a running kst session.
  The constructor creates a connection to either a running
  kst session with name <server_name>, or if none exists, a new one.
  If server_name is not specified, it creates a connection to either the
  kst session with the name ``kstScript``, or if none exists, a new one.

  The Client provides functions which effect the entire kst session,
  provides convenience functions to create objects within kst (eg,
  ``client.new_generated_vector(0, 1, 6)``), and provides
  convenience functions to access objects already within kst (eg,
  ``client.vector("V2")``.  This is the suggested method.

  Alternatively, the constructor for every class inside pykst accepts
  an instance of Client which it uses to interact with a kst session.

  To connect to a kst session named ``kstSession`` (starting kst if necessary)::

      import pykst as kst
      client = kst.Client("kstSession")

  """
  
  def __init__(self,server_name="kstScript"):
    self.ls=QtNetwork.QLocalSocket()
    self.ls.connectToServer(server_name)
    self.ls.waitForConnected(300)
    self.server_name=server_name

    if self.ls.state() == QtNetwork.QLocalSocket.UnconnectedState:
      subprocess.Popen(["kst2","--serverName="+str(server_name)])
      time.sleep(.5)

      while self.ls.state()==QtNetwork.QLocalSocket.UnconnectedState:
        self.ls.connectToServer(server_name)
        self.ls.waitForConnected(300)
    
  def send(self,command):
    """ Sends a command to kst and returns a response. 
    
    You should never use 
    this directly, as there is no guarantee that the internal command
    list kst uses won't change. Instead use the convenience classes 
    included with pykst. 
    """
    self.ls.write(command)
    self.ls.flush()
    self.ls.waitForReadyRead(300000)
    x=self.ls.readAll()
    return x
    
  def send_si(self, handle, command):
    self.send(b2str("beginEdit("+handle+")"))
    x = self.send(command)
    self.send(b2str("endEdit()"))
    return x

  def testCommand(self):
    self.send("testCommand()")

  def clear(self):
    """ Clears all objects from kst.
    
    Equivalent to file->close from the menubar inside kst.  
    """
    self.send("clear()")
    
  def open_kst_file(self, filename):
    """ open a .kst file in kst. """
    self.send("fileOpen("+b2str(filename)+")")

  def save_kst_file(self, filename):
    """ save a .kst file in kst. """
    self.send("fileSave("+b2str(filename)+")")

  def export_graphics_file(self, filename, format=None, width=1280, height=1024, display = 2):
      """
      export the kst session as a set of graphics files.

      :param filename: the name of the file to be saved
      :param format: the format to be used.  if None, the format is determined from the filename extension.
      :param width: width of the plot, in pixels, if required by the display setting.
      :param height: the height of the plot, in pixels, if required by the display setting.
      :param display: how the dimensions are interpreted.

      *display* determines the shape of the plot.  Values are ::

          0   Width set by user, maintain aspect ratio
          1   Height set by user, maintain aspect ratio
          2   Width and Height set by user.
          3   a Width x Width square plot.

      If there is more than one tab, each tab is in a separate file, named
      filename_1.ext, etc.
      """

      if format is None:
          format = os.path.splitext(filename)[1][1:].strip().lower()

      self.send("exportGraphics("+str(filename)+","+str(format)+","+str(width)+","+
                str(height)+","+str(display)+")")


  def screen_back(self):
    """ Equivalent to "Range>Back One Screen" from the menubar inside kst. """
    self.send("screenBack()")
    
  def screen_forward(self):
    """ Equivalent to "Range>Forward One Screen" from the menubar inside kst. """
    self.send("screenForward()")
    
  def count_from_end(self):
    """ Equivalent to "Range>Count From End" from the menubar inside kst. """
    self.send("countFromEnd()")
    
  def read_to_end(self):
    """ Equivalent to "Range>Read To End" from the menubar inside kst. """
    self.send("readToEnd()")
    
  def set_paused(self):
    """ Equivalent to checking "Range>Pause" from the menubar inside kst."""
    self.send("setPaused()")
    
  def unset_paused(self):
    """ Equivalent to unchecking "Range>Pause" from the menubar inside kst."""
    self.send("unsetPaused()")
    
  def tab_count(self):
    """ Get the number of tabs open in the current document. """
    return self.send("tabCount()")
  
  def new_tab(self):
    """ Create a new tab in the current document and switch to it. """
    return self.send("newTab()")
  
  def set_tab(self,tab):
    """ Set the index of the current tab. 
    
    tab must be greater or equal to 0 and less than tabCount(). 
    """
    self.send("setTab("+b2str(tab)+")")

  def set_tab_text(self,new_name):
    """ Set the text of the current tab.

    """
    self.send("renameTab("+new_name+")")

  def cleanup_layout(self, columns="Auto"):
    """ Cleanup layout in the current tab.
    
     If columns is not set, use auto-layout.
     
    """
    self.send("cleanupLayout("+b2str(columns)+")")
  
  def get_scalar_list(self):
    """ returns the scalar names from kst """
    
    x = str(self.send("getScalarList()"))
  
    ret=x.split('|')
    return ret

  def new_generated_string(self, string, name=""):
    """ Create a new generated string in kst.
    
    See :class:`GeneratedString`
    """
    return GeneratedString(self, string, name)

  def generated_string(self, name):
    """ Returns a generated string from kst given its name.
    
    See :class:`GeneratedString`
    """
    return GeneratedString(self, "", name, new=False)
  
  def new_datasource_string(self, filename, field, name=""):
    """ Create a New Data Source String in kst.
    
    See :class:`DataSourceString`
    """
    return DataSourceString(self, filename, field, name)

  def datasource_string(self, name):
    """ Returns a datasource string from kst given its name.
    
    See :class:`DataSourceString`
    """
    return DataSourceString(self, "", "", name, new=False)
  
  def new_generated_scalar(self, value, name=""):
    """ Create a New Generated Scalar in kst.
    
    See :class:`GeneratedScalar`
    """
    return GeneratedScalar(self, value, name)

  def generated_scalar(self, name):
    """ Returns a Generated Scalar from kst given its name.
    
    See :class:`GeneratedScalar`
    """
    return GeneratedScalar(self, "", name, new=False)

  def new_datasource_scalar(self, filename, field, name=""):
    """ Create a New DataSource Scalar in kst.
    
    See :class:`DataSourceScalar`
    """
    return DataSourceScalar(self, filename, field, name)

  def datasource_scalar(self, name):
    """ Returns a DataSource Scalar from kst given its name.
    
    See :class:`DataSourceScalar`
    """
    return DataSourceScalar(self, "", "", name, new=False)

  def new_vector_scalar(self, filename, field, frame=-1, name=""):
    """ Create a New VectorScalar in kst.
    
    See :class:`VectorScalar`
    """
    return VectorScalar(self, filename, field, frame, name)

  def vector_scalar(self, name):
    """ Returns a VectorScalar from kst given its name.
    
    See :class:`VectorScalar`
    """
    return VectorScalar(self, "", "", 0, name, new=False)

  def new_data_vector(self, filename, field, start=0, num_frames=-1,
                 skip=0, boxcarFirst=False, name="") :
    """ Create a New DataVector in kst.
    
    See :class:`DataVector`
    """
    return DataVector(self, filename, field, start, num_frames,
                      skip, boxcarFirst, name)
  
  def data_vector(self, name):
    """ Returns a DataVector from kst given its name.
    
    See :class:`DataVector`
    """
    return DataVector(self, "", "", name=name, new=False)

  def new_generated_vector(self, x0, x1, n, name=""):
    """ Create a New GeneratedVector in kst.
    
    See :class:`GeneratedVector`
    """
    return GeneratedVector(self, x0, x1, n, name)

  def generated_vector(self, name):
    """ Returns a GeneratedVector from kst given its name.
    
    See :class:`GeneratedVector`
    """
    return GeneratedVector(self, 0, 0, 0, name, new=False)
  
  def new_editable_vector(self, np_array = None, name=""):
    """ Create a New Editable Vector in kst.
    
    See :class:`EditableVector`
    """
    return EditableVector(self, np_array, name)

  def editable_vector(self, name):
    """ Returns an Editable Vector from kst given its name.
    
    See :class:`EditableVector`
    """
    return EditableVector(self, None, name, new=False)


  def get_vector_list(self):
    """ returns the vector names from kst """
    
    x = str(self.send("getVectorList()"))
  
    ret=x.split('|')
    return ret

  
  def new_data_matrix(self, filename, field, start_x=0, start_y=0, num_x=-1, num_y=-1, 
                 min_x=0, min_y=0, dx=1, dy=1,name="") :
    """ Create a New DataMatrix in kst.
    
    See :class:`DataMatrix`
    """
    return DataMatrix(self, filename, field, start_x, start_y, num_x, num_y, 
                 min_x, min_y, dx, dy,name)

  def data_matrix(self, name):
    """ Returns a DataMatrix from kst given its name.
    
    See :class:`DataMatrix`
    """
    return DataMatrix(self, "", "", name=name, new=False)

  def new_editable_matrix(self, np_array = None, name=""):
    """ Create a New Editable Matrix in kst.
    
    See :class:`EditableMatrix`
    """
    return EditableMatrix(self, np_array, name)

  def editable_matrix(self, name):
    """ Returns an Editable Matrix from kst given its name.
    
    See :class:`EditableMatrix`
    """
    return EditableMatrix(self, None, name, new=False)
  
  def new_curve(self, x_vector, y_vector, name=""):
    """ Create a New Curve in kst.
    
    See :class:`Curve`
    """
    return Curve(self, x_vector, y_vector, name)

  def curve(self, name):
    """ Returns a Curve from kst given its name.
    
    See :class:`Curve`
    """
    return Curve(self, "", "", name, new=False)

  def new_image(self, matrix, name=""):
    """ Create a new Image in kst.
    
    See :class:`Image`
    """
    return Image(self, matrix, name)

  def image(self, name):
    """ Returns an Image from kst given its name.
    
    See :class:`Image`
    """
    return Image(self, "", "", name, new=False)

  def new_equation(self, x_vector, equation, name=""):
    """ Create a new Equation in kst.
    
    See :class:`Equation`
    """
    return Equation(self, x_vector, equation, name)


  def equation(self, name):
    """ Returns an Equation from kst given its name.
    
    See :class:`Equation`
    """
    return Equation(self, "", "", name, new=False)

  def new_histogram(self, vector, bin_min=0, bin_max=1, num_bins=60, 
                    normalization = 0, auto_bin = True,  name=""):
    """ Create a new histogram in kst.
    
    See :class:`Histogram`
    """
    return Histogram(self, vector, bin_min, bin_max, num_bins, 
                     normalization, auto_bin, name)


  def histogram(self, name):
    """ Returns a histogram from kst given its name.
    
    See :class:`Histogram`
    """
    return Histogram(self, "", 0,0,0, name=name, new=False)

  def new_spectrum(self, 
                   vector, 
                   sample_rate = 1.0, 
                   interleaved_average = False,
                   fft_length = 10,
                   apodize = True, 
                   remove_mean = True, 
                   vector_units = "",
                   rate_units = "Hz",
                   apodize_function = 0,
                   sigma = 1.0,
                   output_type = 0,
                   name=""):
    """ Create a new Spectrum in kst.
    
    See :class:`Spectrum`
    """
    return Spectrum(self, 
                    vector, 
                    sample_rate, 
                    interleaved_average,
                    fft_length,
                    apodize,
                    remove_mean,
                    vector_units,
                    rate_units,
                    apodize_function,
                    sigma,
                    output_type,
                    name)

  def spectrum(self, name):
    """ Returns a spectrum from kst given its name.
    
    See :class:`Spectrum`
    """
    return Spectrum(self, "", name=name, new=False)

  def new_linear_fit(self, x_vector, y_vector, weightvector = 0, name = ""):
    """ Create a New Linear Fit in kst.
    
    See :class:`LinearFit`
    """
    return LinearFit(self, x_vector, y_vector, weightvector, name)

  def linear_fit(self, name):
    """ Returns a linear fit from kst given its name.
    
    See :class:`LinearFit`
    """
    return LinearFit(self, "", "", 0, name, new=False)


  def new_polynomial_fit(self, order, x_vector, y_vector, weightvector = 0, name = ""):
    """ Create a New Polynomial Fit in kst.
    
    See :class:`PolynomialFit`
    """
    return PolynomialFit(self, order, x_vector, y_vector, weightvector, name)

  def polynomial_fit(self, name):
    """ Returns a polynomial fit from kst given its name.
    
    See :class:`PolynomialFit`
    """
    return PolynomialFit(self, 0, "", "", 0, name, new=False)


  def new_flag_filter(self, y_vector, flag, name = ""):
    """ Create a flag filter inside kst.

    See :class:`FlagFilter`
    """
    return FlagFilter(self, y_vector, flag, name)

  def flag_filter(self, name):
    """ Returns a flag_filter from kst given its name.

    See :class:`FlagFilter`
    """
    return FlagFilter(self, "", "", name, new=False)


  def new_label(self, text, pos=(0.5,0.5), rot=0, font_size=12, 
            bold=False, italic=False, font_color="black", 
            font_family="Serif", name="") :
    """ Create a New Label in kst.
    
    See :class:`Label`
    """
    return Label(self, text, pos, rot, font_size, bold, italic, 
                 font_color, font_family, name)

  def label(self, name):
    """ Returns a Label from kst given its name.
    
    See :class:`Label`
    """
    return Label(self, "", name=name, new=False)
  
  def new_box(self, pos=(0.1,0.1), size=(0.1,0.1), rot=0, 
          fill_color="white", fill_style=1, stroke_style=1, stroke_width=1,
          stroke_brush_color="black", stroke_brush_style=1, 
          strokeJoinStyle=1, stroke_cap_style=1, fix_aspect=False, name="") :
    """ Create a New Box in kst.
    
    See :class:`Box`
    """
    return Box(self, pos, size, rot, fill_color, fill_style, stroke_style, 
               stroke_width, stroke_brush_color, stroke_brush_style, 
               strokeJoinStyle, stroke_cap_style, fix_aspect, name)

  def box(self, name):
    """ Returns a Box from kst given its name.
    
    See :class:`Box`
    """
    return Box(self, name=name, new=False)
  
  def new_legend(self, plot, name = "") :
    """ Create a new Legend in a plot in kst.

    See :class:'Legend'
    """
    return Legend(self, plot, name)

  def legend(self, name):
    """ Returns a Legend from kst given its name.

    See :class:`Legend`
    """
    return Legend(self, name=name, new=False)

  def new_circle(self, pos=(0.1, 0.1), diameter=0.1,
             fill_color="white",fill_style=1,stroke_style=1,
             stroke_width=1,stroke_brush_color="grey",stroke_brush_style=1, name="") :
    """ Create a New Circle in kst.
    
    See :class:`Circle`
    """
    return Circle(self, pos, diameter, fill_color, fill_style, stroke_style, 
                  stroke_width, stroke_brush_color, stroke_brush_style, name)
  
  def circle(self, name):
    """ Returns a Circle from kst given its name.
    
    See :class:`Circle`
    """
    return Circle(self, name=name, new=False)
  
  def new_ellipse(self,pos=(0.1,0.1), size=(0.1,0.1),
               rot=0, fill_color="white", fill_style=1, stroke_style=1,
               stroke_width=1, stroke_brush_color="black", stroke_brush_style=1,
               fix_aspect=False, name="") :
    """ Create a New Ellipse in kst.
    
    See :class:`Ellipse`
    """
    return Ellipse(self,pos, size, rot, fill_color, fill_style, stroke_style, 
                   stroke_width, stroke_brush_color, stroke_brush_style, 
                   fix_aspect, name)

  def ellipse(self, name):
    """ Returns an ellipse from kst given its name.
    
    See :class:`Ellipse`
    """
    return Ellipse(self, name=name, new=False)
  
  def new_line(self,pos=(0.1,0.1),length=0.1,rot=0,
           stroke_style=1,stroke_width=1,stroke_brush_color="black",
           stroke_brush_style=1,stroke_cap_style=1, name="") :
    """ Create a New Line in kst.
    
    See :class:`Line`
    """
    return Line(self,pos, length, rot, stroke_style, stroke_width, 
                stroke_brush_color, stroke_brush_style, stroke_cap_style, name)
  
  def line(self, name):
    """ Returns a Line from kst given its name.
    
    See :class:`Line`
    """
    return Line(self, name=name, new=False)

  def new_arrow(self,pos=(0.1,0.1), length=0.1, rot=0, 
            arror_at_start = False, arrow_at_end = True, arrow_size = 12.0, 
            stroke_style=1, stroke_width=1, stroke_brush_color="black",
            stroke_brush_style=1, stroke_cap_style=1, name="") :
    """ Create a New Arrow in kst.
    
    See :class:`Arrow`
    """
    return Arrow(self,pos, length, rot, arror_at_start, arrow_at_end, arrow_size, 
          stroke_style, stroke_width, stroke_brush_color, stroke_brush_style, 
          stroke_cap_style, name)
    
  def arrow(self, name):
    """ Returns an Arrow from kst given its name.
    
    See :class:`Arrow`
    """
    return Arrow(self, name=name, new=False)
    
  def new_picture(self,filename,pos=(0.1,0.1), width=0.1,rot=0, name="") :
    """ Create a New Picture in kst.
    
    See :class:`Picture`
    """
    return Picture(self,filename, pos, width, rot, name)
  
  def picture(self, name):
    """ Returns a Picture from kst given its name.
    
    See :class:`Picture`
    """
    return Picture(self, "", name = name, new=False)
  
  def new_SVG(self, filename, pos=(0.1,0.1), width=0.1, rot=0, name="") :
    """ Create a New SVG in kst.
    
    See :class:`SVG`
    """
    return SVG(self, filename, pos, width, rot, name)
  
  def SVG(self, name):
    """ Returns a SVG from kst given its name.
    
    See :class:`SVG`
    """
    return SVG(self, "", name = name, new=False)

  def new_plot(self,pos=(0.1,0.1),size=(0,0),rot=0,font_size = 0, columns=0,
           fill_color="white", fill_style=1, stroke_style=1, stroke_width=1,
           stroke_brush_color="black", stroke_brush_style=1, 
           strokeJoinStyle=1, stroke_cap_style=1, fix_aspect=False, name="") :
    """ Create a New Plot in kst.
    
    See :class:`Plot`
    """
    return Plot(self, pos, size, rot, font_size, columns, fill_color, fill_style, stroke_style,
                stroke_width, stroke_brush_color, stroke_brush_style, 
                strokeJoinStyle, stroke_cap_style, fix_aspect, name)
  
  def plot(self, name):
    """ Returns a Plot from kst given its name.
    
    See :class:`Plot`
    """
    return Plot(self, name = name, new=False)

  def set_datasource_option(self, option, value, filename, data_source="Ascii File"):
    """ Sets the value of a data source configuration option.

    :param option: the name of the option - eg ""Data Start"
    :param value: True or False
    :param filename: the name of the file or 0 to set global default
    :param data_source: the type of data source

    Examples:

    Tell kst that trial1.csv is a file with the field names in row 1 and units in row 2::

        import pykst as kst
        client = kst.Client()
        client.set_datasource_option("Column Delimiter", ",", "trial1.csv")
        client.set_datasource_option("Column Type", 2, "trial1.csv")
        client.set_datasource_option("Data Start", 3-1, "trial1.csv")
        client.set_datasource_option("Fields Line", 1-1, "trial1.csv")
        client.set_datasource_option("Read Fields", True, "trial1.csv")
        client.set_datasource_option("Units Line", 2-1, "trial1.csv")
        client.set_datasource_option("Read Units", True, "trial1.csv")

    Configuration options supported by the ASCII data source (default) are::

        "ASCII Time format"
        "Column Delimiter"
        "Column Type"
        "Column Width"
        "Column Width is const"
        "Comment Delimiters"
        "Data Rate for index"
        "Data Start"
        "Default INDEX Interpretation"
        "Fields Line"
        "Filename Pattern"
        "Index"
        "Limit file buffer size"
        "NaN value"
        "Read Fields"
        "Read Units"
        "Size of limited file buffer"
        "Units Line"
        "Use Dot"
        "Use threads when parsing Ascii data"
        "date/time offset"
        "relative offset"
        "updateType"
        "use an explicit date/time offset"
        "use file time/date as offset"
        "use relative file time offset"


    """

    if (filename == 0):
      filename = "$DEFAULT"

    if isinstance(value, bool):
      self.send("setDatasourceBoolConfig("+data_source+","+filename+","+option+","+b2str(value)+")")
    elif isinstance(value, int):
      self.send("setDatasourceIntConfig("+data_source+","+filename+","+option+","+str(value)+")")
    else:
      v = value
      v.replace(',', '`')
      self.send("setDatasourceStringConfig("+data_source+","+filename+","+option+","+str(v)+")")



class NamedObject:
    """ Convenience class. You should not use it directly."""
    def __init__(self,client):
      self.client=client
      
    def set_name(self,name):
      """ Set the name of the object inside kst. """
      self.client.send_si(self.handle, b2str("setName("+b2str(name)+")"))
      
    def name(self):
      """ Returns the name of the object from inside kst. """
      return self.client.send_si(self.handle, "name()")

    def description_tip(self):
      """  Returns a string describing the object """
      return self.client.send_si(self.handle, "descriptionTip()")

    def test_command(self):
      return self.client.send_si(self.handle, "testCommand()")

 
class Object(NamedObject) :
  """ Convenience class. You should not use it directly."""
  def __init__(self,client) :
    NamedObject.__init__(self,client)

  def type_str(self):
    """ Returns the type of the object from inside kst. """
    return self.client.send_si(self.handle, "type()")


class String(Object) :
  """ Convenience class. You should not use it directly."""
  def __init__(self,client) :
    Object.__init__(self,client)

  def value(self) :
    """ Returns the string. """
    return self.client.send_si(self.handle, "value()")

class GeneratedString(String) :
  """ A string constant inside kst.
  
  This class represents a string you would create via 
  "Create>String>Generated" from the menubar inside kst.

  :param string: The value of the string.

  To import the string "Hello World" into kst::

    import pykst as kst
    client = kst.Client()
    s = client.new_generatedString("Hello World")
    
  """
  def __init__(self,client,string,name="", new=True) :
    String.__init__(self,client)

    if (new == True):
      self.client.send("newGeneratedString()")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)

      self.set_value(string)
      self.set_name(name)
    else:
      self.handle = name

  def set_value(self,val):
    """ set the value of the string inside kst. """
    self.client.send_si(self.handle, b2str("setValue("+b2str(val)+")"))

class DataSourceString(String) :
  """ A string read from a data source inside kst.
  
  This class represents a string you would create via 
  "Create>String>Read from Data Source" from the menubar inside kst.
  
  :param filename: The name of the file/data source to read the string from.
  :param field: the name of the field in the data source.

  To read "File path" from the data source "tmp.dat" into kst::
  
    import pykst as kst
    client = kst.Client()
    s = client.new_datasource_string("tmp.dat", "File Path")
    
  """
  def __init__(self,client,filename,field,name="", new=True) :
    String.__init__(self,client)
    
    if (new == True):
      self.client.send("newDataString()")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)
      self.change(filename, field)
    else:
      self.handle = name

  def change(self,filename,field):
    """ Change a DataSource String.
    
    Change the file and field of a DataSourceString in kst.
    
    :param filename: The name of the file/data source to read the string from.
    :param field: the name of the field in the data source.
    """
    self.client.send_si(self.handle, b2str("change("+b2str(filename)+","+b2str(field)+")"))


class Scalar(Object) :
  """ Convenience class. You should not use it directly."""
  def __init__(self,client) :
    Object.__init__(self,client)

  def value(self) :
    """ Returns the scalar. """
    return self.client.send_si(self.handle, "value()")

class GeneratedScalar(Scalar) :
  """ A scalar constant inside kst.
 
  This class represents a scalar you would create via 
  "Create>Scalar>Generate" from the menubar inside kst.

  :param value: the value to assign to the scalar constant.
  
  To import the scalar of value 42 into kst::

    import pykst as kst
    client = kst.Client()
    s = client.new_generated_scalar(42)
    
  """
  def __init__(self, client, value, name="", new=True) :
    Scalar.__init__(self,client)

    if (new == True):
      self.client.send("newGeneratedScalar()")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)

      self.set_value(value)
      self.set_name(name)
    else:
      self.handle = name      

  def set_value(self,val):
    """ set the value of the string inside kst. """
    self.client.send_si(self.handle, b2str("setValue("+b2str(val)+")"))


class DataSourceScalar(Scalar) :
  """ A scalar read from a data source inside kst.
  
  This class represents a scalar you would create via 
  "Create>Scalar>Read from Data Source" from the menubar inside kst.
 
  :param filename: The name of the file/data source to read the scalar from.
  :param field: the name of the field in the data source.
 
  To read "CONST1" from the data source "tmp.dat" into kst::
  
    import pykst as kst
    client = kst.Client()
    x = client.new_datasource_scalar("tmp.dat", "CONST1")
    
  """
  def __init__(self,client,filename,field,name="", new=True) :
    Scalar.__init__(self,client)
    
    if (new == True):
      self.client.send("newDataScalar()")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)

      self.change(filename, field)
    else:
      self.handle = name      

  def change(self,filename,field):
    """ Change a DataSource Scalar.
    
    Change the file and field of a DataSourceScalar in kst.
    
    :param filename: The name of the file/data source to read the scalar from.
    :param field: the name of the field in the data source.
    """
    self.client.send_si(self.handle, "change("+filename+","+field+")")

  def file(self) :
    """ Returns the the data source file name. """
    return self.client.send_si(self.handle, "file()")

  def field(self) :
    """ Returns the field. """
    return self.client.send_si(self.handle, "field()")


class VectorScalar(Scalar) :
  """ A scalar in kst read from a vector from a data source.
  
  This class represents a scalar you would create via 
  "Create>Scalar>Read from vector" from the menubar inside kst.
  
  :param filename: The name of the file/data source to read the scalar from.
  :param field: the name of the vector in the data source.  
  :param frame: which frame of the vector to read the scalar from. 
                frame = -1 (the default) reads from the end of the file.
  
  To read the last value of the vector INDEX from the file "tmp.dat"
  into kst::

    import pykst as kst
    client = kst.Client()
    x = client.new_vector_scalar("tmp.dat", "INDEX", -1)

  """
  def __init__(self, client, filename, field, frame=-1, name="", new=True) :
    Scalar.__init__(self,client)

    if (new == True):    
      self.client.send("newVectorScalar()")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)

      self.change(filename, field, frame)
    else:
      self.handle = name      

  def change(self,filename,field,frame):
    """ Change a Vector Scalar in kst.
    
    Change the file, field and frame of a VectorScalar in kst.
    
    :param filename: The name of the file/data source to read the scalar from.
    :param field: the name of the vector in the data source.  
    :param frame: which frame of the vector to read the scalar from.   
                  frame = -1 reads from the end of the file.
    """
    self.client.send_si(self.handle, b2str("change("+b2str(filename)+","+b2str(field)+","+b2str(frame)+")"))

  def file(self) :
    """ Returns the the data source file name. """
    return self.client.send_si(self.handle, "file()")

  def field(self) :
    """ Returns the field. """
    return self.client.send_si(self.handle, "field()")

  def frame(self) :
    """ Returns the fame. """
    return self.client.send_si(self.handle, "frame()")

class VectorBase(Object):
  """ Convenience class. You should not use it directly."""
  def __init__(self,client) :
    Object.__init__(self,client)

  def value(self,index):
    """  Returns element i of this vector. """
    return self.client.send_si(self.handle, "value("+b2str(index)+")")

  def length(self):
    """  Returns the number of samples in the vector. """
    return self.client.send_si(self.handle, "length()")

  def min(self):
    """  Returns the minimum value in the vector. """
    return self.client.send_si(self.handle, "min()")

  def mean(self):
    """  Returns the mean of the vector. """
    return self.client.send_si(self.handle, "mean()")

  def max(self):
    """  Returns the maximum value in the vector. """
    return self.client.send_si(self.handle, "max()")

  def get_numpy_array(self) :
    """ get a numpy array which contains the kst vector values """
    with tempfile.NamedTemporaryFile() as f:
      self.client.send_si(self.handle, "store(" + f.name + ")")
      array = fromfile(f.name, dtype = float64)
      
    return array


class DataVector(VectorBase):
  """ A vector in kst, read from a data source.
  
  This class represents a vector you would create via 
  "Create>Vector>Read from Data Source" from the menubar inside kst.

  The parameters of this function mirror the parameters within 
  "Create>Vector>Read from Data Source".

  :param filename: The name of the file/data source to read the scalar from.
  :param field: the name of the vector in the data source.  
  :param start: The starting index of the vector.  
                start = -1 for count from end.
  :param num_frames: The number of frames to read.  
                  num_frames = -1 for read to end.
  :param skip: The number of frames per sample read.  
               skip = 0 to read every sample.
  :param boxcarFirst: apply a boxcar filter before skiping.
  
  To create a vector from "tmp.dat" with field "INDEX" from 
  frame 3 to frame 10, reading a sample every other frame without 
  a boxcar filter::

    import pykst as kst
    client = kst.Client()
    v = client.new_data_vector("tmp.dat", "INDEX", 3, 10, 2, False) 
    
  """
  def __init__(self, client, filename, field, start=0, num_frames=-1,
               skip=0, boxcarFirst=False, name="", new=True) :
    VectorBase.__init__(self,client)

    if (new == True):
      self.client.send("newDataVector()")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)
      self.change(filename, field, start, num_frames, skip, boxcarFirst)
    else:
      self.handle = name

  def change(self, filename, field, start, num_frames, skip, boxcarFirst):
    """ Change the parameters of a data vector.
    
    :param filename: The name of the file/data source to read the scalar from.
    :param field: the name of the vector in the data source.  
    :param start: The starting index of the vector.  
                  start = -1 for count from end.
    :param num_frames: The number of frames to read.  
                    num_frames = -1 for read to end.
    :param skip: The number of frames per sample read.  
                skip = 0 to read every sample.
    :param boxcarFirst: apply a boxcar filter before skiping.
    
    """
    self.client.send_si(self.handle, "change("+filename+","+field+","
                        +b2str(start)+","+b2str(num_frames)+","+b2str(skip)
                        +","+b2str(boxcarFirst)+")")

  def field(self):
    """  Returns the fieldname. """
    return self.client.send_si(self.handle, "field()")

  def filename(self):
    """  Returns the filename. """
    return self.client.send_si(self.handle, "filename()")

  def start(self):
    """  Returns the index of first frame in the vector.  
    -1 means count from end. """
    return self.client.send_si(self.handle, "start()")

  def n_frames(self):
    """  Returns the number of frames to be read. -1 means read to end. """
    return self.client.send_si(self.handle, "NFrames()")

  def skip(self):
    """  Returns number of frames to be skipped between samples read. """
    return self.client.send_si(self.handle, "skip()")

  def boxcar_first(self):
    """  True if boxcar filtering has been applied before skipping. """
    return self.client.send_si(self.handle, "boxcarFirst()")

class GeneratedVector(VectorBase):
  """ Create a generated vector in kst.
  
  This class represents a vector you would create via 
  "Create>Vector>Generate" from the menubar inside kst.

  :param x0: The first value in the vector.
  :param x1: The last value in the vector.
  :param n: The number of evenly spaced values in the vector.

  To create the vector {0, 0.2, 0.4, 0.6, 0.8, 1.0}::

    import pykst as kst
    client = kst.Client()
    v = client.new_generated_vector(0, 1, 6) 
    
  """
  def __init__(self, client, x0, x1, n, name="", new=True) :
    VectorBase.__init__(self,client)

    if (new == True):
      self.client.send("newGeneratedVector()")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)

      self.change(x0, x1, n)
      self.set_name(name)
    else:
      self.handle = name      

  def change(self,x0, x1, n):
    """ Change the parameters of a Generated Vector inside kst.
    
    :param x0: The first value in the vector.
    :param x1: The last value in the vector.
    :param n: The number of evenly spaced values in the vector.
    """
    self.client.send_si(self.handle, "change("+b2str(x0)+","+b2str(x1)+
                        ","+b2str(n)+")")

class EditableVector(VectorBase):
  """ A vector in kst, which is editable from python.
  
  This vector in kst can be created from a numpy array,
  (with ''load()'') or edited point by point (with ''setValue()'').
  "Create>Vector>Generate" from the menubar inside kst.

  :param np_array: initialize the vector in kst to this (optional) 1D numpy array.
  To create a from the num py array np::

    import pykst as kst
    client = kst.Client()
    v = client.new_editable_vector(np)
    
  """
  def __init__(self, client, np_array = None, name="", new=True) :
    VectorBase.__init__(self,client)

    if (new == True):
      self.client.send("newEditableVector()")
      if (np_array != None) :
        assert(np_array.dtype == float64)
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
          f.close()
          atexit.register(cleanTmpFile, f)
          np_array.tofile(f.name)
          self.client.send("load(" + f.name + ")")        

      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)

      self.set_name(name)
    else:
      self.handle = name      

  def load(self, np_array):
    """  sets the value of the vector to that of the float64
    1D np array """
    
    assert(np_array.dtype == float64)
    with tempfile.NamedTemporaryFile(delete=False) as f:
      f.close()
      atexit.register(cleanTmpFile, f)
      np_array.tofile(f.name)
      retval = self.client.send_si(self.handle, "load(" + f.name + ")")        
      
    return retval

class Matrix(Object):
  """ Convenience class. You should not use it directly."""
  def __init__(self,client) :
    Object.__init__(self,client)

  def value(self,i_x, i_y):
    """  Returns element (i_x, i_y} of this matrix. """
    return self.client.send_si(self.handle, "value("+b2str(i_x)+
                               ","+b2str(i_y)+")")

  def length(self):
    """  Returns the number of elements in the matrix. """
    return self.client.send_si(self.handle, "length()")

  def min(self):
    """  Returns the minimum value in the matrix. """
    return self.client.send_si(self.handle, "min()")

  def mean(self):
    """  Returns the mean of the matrix. """
    return self.client.send_si(self.handle, "mean()")

  def max(self):
    """  Returns the maximum value in the matrix. """
    return self.client.send_si(self.handle, "max()")

  def width(self):
    """  Returns the X dimension of the matrix. """
    return self.client.send_si(self.handle, "width()")

  def height(self):
    """  Returns the Y dimension of the matrix. """
    return self.client.send_si(self.handle, "height()")

  def dx(self):
    """  Returns the X spacing of the matrix, for when the matrix is used in an image. """
    return self.client.send_si(self.handle, "dX()")

  def dy(self):
    """  Returns the Y spacing of the matrix, for when the matrix is used in an image. """
    return self.client.send_si(self.handle, "dY()")

  def min_x(self):
    """  Returns the minimum X location of the matrix, for when the matrix is used in an image. """
    return self.client.send_si(self.handle, "minX()")

  def min_y(self):
    """  Returns the minimum X location of the matrix, for when the matrix is used in an image. """
    return self.client.send_si(self.handle, "minY()")
    
  def get_numpy_array(self) :
    """ get a numpy array which contains the kst matrix values """
    with tempfile.NamedTemporaryFile() as f:
      args = str(self.client.send_si(self.handle, "store(" + f.name + ")"))
      dims = tuple(map(int, args.split()))
      array = fromfile(f.name, dtype = float64)
      array = array.reshape((dims))
      
    return array


class DataMatrix(Matrix):
  """  Create a Data Matrix which reads from a data source inside kst.
  
  This class represents a matrix you would create via 
  "Create>Vector>Read from Data Source" from the menubar inside kst.
  The parameters of this function mirror the parameters within 
  "Create>Matrix>Read from Data Source".

  :param filename: The name of the file/data source to read the scalar from.
  :param field: the name of the vector in the data source.  
  :param start_x/start_y: the x/y index to start reading from. start_x/Y = -1 
                   to count from the right/bottom.
  :param num_x/num_y: the number of columns/rows to read.  num_x/Y = -1 to read
               to the end.
  :param min_x/min_y: Hint to Images of the coordinates corresponding to the
                 the left/bottom of the Matrix
  :param dx/dy: Hint to Images of the spacing between points.

  To create a matrix from 'foo.png' with field '1'::
  
    import pykst as kst
    client = kst.Client()
    v = client.new_data_matrix("foo.png", "1") 
    
  """
  def __init__(self,client,filename,field,start_x=0,start_y=0,num_x=-1,num_y=-1,
               min_x=0, min_y=0, dx=1, dy=1,name="", new=True) :
    Matrix.__init__(self,client)

    if (new == True):
      self.client.send("newDataMatrix()")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)

      self.change(filename,field,start_x,start_y,num_x,num_y,min_x,min_y,dx,dy)
    else:
      self.handle = name      

  def change(self,filename,field,start_x=0,start_y=0,num_x=-1,num_y=-1,
             min_x=0, min_y=0, dx=1, dy=1):
    """ Change the parameters if a Data Matrix inside kst.
    
    :param filename: The name of the file/data source to read the scalar from.
    :param field: the name of the vector in the data source.  
    :param start_x/start_y: the x/y index to start reading from. start_x/y = -1 
                    to count from the right/bottom.
    :param num_x/num_y: the number of columns/rows to read.  num_x/Y = -1 to read
                to the end.
    :param min_x/min_y: Hint to Images of the coordinates corresponding to the
                  the left/bottom of the Matrix
    :param dx/dy: Hint to Images of the spacing between points.
    """    
    self.client.send_si(self.handle, "change("+b2str(filename)+","+
                        b2str(field)+","+b2str(start_x)+","+
                        b2str(start_y)+","+b2str(num_x)+","+b2str(num_y)+","+
                        b2str(min_x)+","+b2str(min_y)+","+b2str(dx)+","+
                        b2str(dy)+")")

  def field(self):
    """  Returns the fieldname. """
    return self.client.send_si(self.handle, "field()")

  def filename(self):
    """  Returns the filename. """
    return self.client.send_si(self.handle, "filename()")

  def start_x(self):
    """  Returns the X index of the matrix in the file """
    return self.client.send_si(self.handle, "startX()")

  def start_y(self):
    """  Returns the Y index of the matrix in the file """
    return self.client.send_si(self.handle, "startY()")

class EditableMatrix(Matrix):
  """ A matrix in kst, which is editable from python.
  
  This matrix in kst can be created from 2D float64 numpy array,
  (with ''load()'') or edited point by point (with ''setValue()'').

  :param np_array: initialize the matrix in kst to this 2D numpy array.
  
  To create an editable matrix from the num py array np::

    import pykst as kst
    client = kst.Client()
    m = client.new_editable_matrix(np)
    
  """
  def __init__(self, client, np_array = None, name="", new=True) :
    Matrix.__init__(self,client)

    if (new == True):
      self.client.send("newEditableMatrix()")
      if (np_array != None) :
        assert(np_array.dtype == float64)
        nx = np_array.shape[0]
        ny = np_array.shape[1]

        with tempfile.NamedTemporaryFile(delete=False) as f:
          f.close()
          atexit.register(cleanTmpFile, f)
          np_array.tofile(f.name)
          self.client.send("load(" + f.name + ","+b2str(nx)+","+b2str(ny)+")")

      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)

      self.set_name(name)
    else:
      self.handle = name      

  def load(self, np_array):
    """  sets the values of the matrix in kst to that of the float64
    2D np array """
    
    assert(np_array.dtype == float64)
    nx = np_array.shape[0]
    ny = np_array.shape[1]
    
    with tempfile.NamedTemporaryFile(delete=False) as f:
      f.close()
      atexit.register(cleanTmpFile, f)
      np_array.tofile(f.name)
      retval = self.client.send_si(self.handle, "load(" + f.name + ","+b2str(nx)+","+b2str(ny)+")")        
      
    return retval


class Relation(Object):
  """ Convenience class. You should not use it directly."""
  def __init__(self,client) :
    Object.__init__(self,client)

  def max_x(self):
    """  Returns the max X value of the curve or image. """
    return self.client.send_si(self.handle, "maxX()")

  def min_x(self):
    """  Returns the min X value of the curve or image. """
    return self.client.send_si(self.handle, "minX()")

  def max_y(self):
    """  Returns the max Y value of the curve or image. """
    return self.client.send_si(self.handle, "maxY()")

  def min_y(self):
    """  Returns the min Y value of the curve or image. """
    return self.client.send_si(self.handle, "minY()")

  def show_edit_dialog(self):
    """  shows the edit dialog for the curve or image. """
    return self.client.send_si(self.handle, "showEditDialog()")

class Curve(Relation):
  """ A Curve inside kst.
  
  This class represents a string you would create via 
  "Create>Curve" from the menubar inside kst.  The parameters of this 
  function mirror the parameters within "Create>Curve".

  :param x_vector: The vector which specifies the X coordinates of each point.
  :param x_vector: The vector which specifies the Y coordinates of each point.
  
  Use the convenience function in client to create a curve in kst session 
  "client" of vectors v1 and v2::
  
    c1 = client.new_curve(v1, v2)
  
  """
  def __init__(self,client, x_vector, y_vector, name="", new=True) :
    Relation.__init__(self,client)

    if (new == True):
      self.client.send("newCurve()")
      self.client.send("setXVector("+x_vector.handle+")")
      self.client.send("setYVector("+y_vector.handle+")")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)
      self.set_name(name)
    else:
      self.handle = name      

  def set_y_error(self,vector, vectorminus=0):
    """ Set the Y Error flags for the curve.  
    
    The error bars are symetric if vectorminus is not set. 
    """
    self.client.send("beginEdit("+self.handle+")")

    self.client.send("setYError("+vector.handle+")")
    if vectorminus != 0:
      self.client.send("setYMinusError("+vectorminus.handle+")")
    else:
      self.client.send("setYMinusError("+vector.handle+")")

    self.client.send("endEdit()")

  def set_x_error(self,vector, vectorminus=0):
    """ Set the X Error flags for the curve.  
    
    The error bars are symetric if vectorminus is not set.  
    """
    self.client.send("beginEdit("+self.handle+")")

    self.client.send("setXError("+vector.handle+")")
    if vectorminus != 0:
      self.client.send("setXMinusError("+vectorminus.handle+")")
    else:
      self.client.send("setXMinusError("+vector.handle+")")

    self.client.send("endEdit()")

  def set_color(self,color):
    """ Set the color of the points and lines.  
    
    Colors are given by a name such as ``red`` or a hex number such 
    as ``#FF0000``. 
    """
    self.client.send_si(self.handle, "setColor("+color+")")

  def set_head_color(self,color):
    """ Set the color of the Head marker, if any.  
    
    Colors are given by a name such as ``red`` or a hex number such 
    as ``#FF0000``. 
    """
    self.client.send_si(self.handle, "setHeadColor("+color+")")

  def set_bar_fill_color(self,color):
    """ Set the fill color of the histogram bars, if any.  
    
    Colors are given by a name such as ``red`` or a hex number such 
    as ``#FF0000``. 
    """
    self.client.send_si(self.handle, "setBarFillColor("+color+")")

  def set_has_points(self,has=True):
    """ Set whether individual points are drawn on the curve """
    if (has == True):
      self.client.send_si(self.handle, "setHasPoints(True)")
    else:
      self.client.send_si(self.handle, "setHasPoints(False)")

  def set_has_bars(self,has=True):
    """ Set whether histogram bars are drawn. """
    if (has == True):
      self.client.send_si(self.handle, "setHasBars(True)")
    else:
      self.client.send_si(self.handle, "setHasBars(False)")

  def set_has_lines(self,has=True):
    """ Set whether lines are drawn. """
    if (has == True):
      self.client.send_si(self.handle, "setHasLines(True)")
    else:
      self.client.send_si(self.handle, "setHasLines(False)")

  def set_has_head(self,has=True):
    """ Set whether a point at the head of the line is drawn """
    if (has == True):
      self.client.send_si(self.handle, "setHasHead(True)")
    else:
      self.client.send_si(self.handle, "setHasHead(False)")

  def set_line_width(self,x):
    """ Sets the width of the curve's line. """
    self.client.send_si(self.handle, "setLineWidth("+b2str(x)+")")

  def set_point_size(self,x):
    """ Sets the size of points, if they are drawn. """
    self.client.send_si(self.handle, "setPointSize("+b2str(x)+")")

  def set_point_density(self,density):
    """ Sets the point density.  
    
    When show_points is true, this option can be used to only show a
    subset of the points, for example, to use point types to discriminate
    between different curves..  This does not effect 'lines', where every
    point is always connected.
    
    density can be from 0 (all points) to 4. 
    """
    self.client.send_si(self.handle, "setPointDensity("+b2str(density)+")")

  def set_point_type(self,point_type):
    """ Sets the point type.  
    
    The available point types are:: 
    
     0:  X                       1: open square 
     2:  open circle,            3: filled circle
     4:  downward open triangle  5: upward open triangle
     6:  filled square           7: + 
     8:  *                       9: downward filled triangle
     10: upward filled triangle 11: open diamond
     12: filled diamond
    
    """
    self.client.send_si(self.handle, "setPointType("+b2str(point_type)+")")

  def set_head_type(self,x):
    """ Sets the head point type.  See set_point_type for details."""
    self.client.send_si(self.handle, "setHeadType("+b2str(x)+")")

  def set_line_style(self,lineStyle):
    """ Sets the line type.  
    
    0 is SolidLine, 1 is DashLine, 2 is DotLine, 3 is DashDotLine, 
    and 4 isDashDotDotLine,
    """
    self.client.send_si(self.handle, "setLineStyle("+b2str(lineStyle)+")")


  def color(self):
    """ Returns the curve color. """
    return self.client.send_si(self.handle, "color()")

  def head_color(self):
    """ Returns the curve head color. """
    return self.client.send_si(self.handle, "headColor()")

  def bar_fill_color(self):
    """ Returns the bar fill color. """
    return self.client.send_si(self.handle, "barFillColor()")

  def has_points(self):
    """ Returns True if the line has points. """
    return (self.client.send_si(self.handle, "hasPoints()")=="True")

  def has_lines(self):
    """ Returns True if the line has lines. """
    return (self.client.send_si(self.handle, "hasLines()")=="True")

  def has_bars(self):
    """ Returns True if the line has historgram bars. """
    return (self.client.send_si(self.handle, "hasBars()")=="True")

  def has_head(self):
    """ Returns True if the last point has a special marker. """
    return (self.client.send_si(self.handle, "hasHead()")=="True")

  def line_width(self):
    """ Returns the width of the line. """
    return self.client.send_si(self.handle, "lineWidth()")

  def point_size(self):
    """ Returns the size of the points. """
    return self.client.send_si(self.handle, "pointSize()")

  def point_type(self):
    """ Returns index of the point type.  See set_point_type. """
    return self.client.send_si(self.handle, "pointType()")

  def head_type(self):
    """ Returns index of the head point type.  See set_point_type. """
    return self.client.send_si(self.handle, "headType()")

  def line_style(self):
    """ Returns the index of the line style.  See set_line_style. """
    return self.client.send_si(self.handle, "lineStyle()")

  def point_density(self):
    """ Returns the density of points shown.  see set_point_density.  """
    return self.client.send_si(self.handle, "pointDensity()")

  def x_vector(self):
    """ Returns the x vector of the curve.
    
    FIXME: should figure out what kind of vector this is and return that.
    """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "xVector()")
    return vec

  def y_vector(self):
    """ Returns the y vector of the curve.
    
    FIXME: should figure out what kind of vector this is and return that.
    """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "yVector()")
    return vec

  def x_error_vector(self):
    """ Returns the +x error vector of the curve.
    
    FIXME: should figure out what kind of vector this is and return that.
    """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "xErrorVector()")
    return vec

  def y_error_vector(self):
    """ Returns the +y error vector of the curve.
    
    FIXME: should figure out what kind of vector this is and return that.
    """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "yErrorVector()")
    return vec

  def x_minus_error_vector(self):
    """ Returns the -x error vector of the curve.
    
    FIXME: should figure out what kind of vector this is and return that.
    """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "xMinusErrorVector()")
    return vec

  def y_minus_error_vector(self):
    """ Returns the -y error vector of the curve.
    
    FIXME: should figure out what kind of vector this is and return that.
    """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "yMinusErrorVector()")
    return vec

class Image(Relation):
  """ An image inside kst.
  
  This class represents an image you would create via 
  "Create>Image" from the menubar inside kst.  The parameters of this 
  function mirror the parameters within "Create>Curve".

  :param matrix: The matrix which defines the image.
  
  Use the convenience function in client to create an image in kst session 
  "client" of Matrix m::
  
    i1 = client.new_image(m)
  
  """
  def __init__(self,client, matrix, name="", new=True) :
    Relation.__init__(self,client)

    if (new == True):
      self.client.send("newImage()")
      self.client.send("setMatrix("+matrix.handle+")")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)
      self.set_name(name)

    else:
      self.handle = name      

  def set_matrix(self, matrix):
    """ change the matrix which is the source of the image. """
    self.client.send_si(self.handle, "setMatrix("+matrix.handle+")")

  def set_palette(self, palette):
    """ set the palette, selected by index.
    
    The available palettes are::
    
      0: Grey
      1:  Red 
      2:  Spectrum
      3:  EOS-A
      4:  EOS-B
      5:  8 colors
      6:  Cyclical Spectrum
    
    Note: this is not the same order as the dialog.
    """
    self.client.send_si(self.handle, "setPalette("+b2str(palette)+")")
    
  def set_range(self, zmin, zmax):
    """ sets the z range of the color map."""
    self.client.send_si(self.handle, "setFixedColorRange("+
                        b2str(zmin)+","+b2str(zmax)+")")
  
  def set_auto_range(self, saturated=0):
    """ Automatically set the z range of the color map
    
    :param saturated: The colormap range is set so that this fraction
                      of the points in the matrix are saturated.
    
    Equal numbers of points are saturated at both ends of the color map.
    """
    self.client.send_si(self.handle, "setAutoColorRange("+b2str(saturated) + ")")
    
  def max_z(self):
    """  Returns the max Z value of the curve or image. """
    return self.client.send_si(self.handle, "maxZ()")

  def min_z(self):
    """  Returns the max Z value of the curve or image. """
    return self.client.send_si(self.handle, "minZ()")

# Equation ############################################################
class Equation(Object) : 
  """ An equation inside kst.
   
    :param xvector: the x vector of the equation
    :param equation: the equation
    
    Vectors inside kst are refered to as [vectorname] or [scalarname].
  """
  def __init__(self, client, xvector, equation, name="", new=True) :
    Object.__init__(self,client)
    
    if (new == True):      
      self.client.send("newEquation()")

      self.client.send("setEquation(" + equation + ")")
      self.client.send("setInputVector(X,"+xvector.handle+")")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)
      self.set_name(name)
    else:
      self.handle = name

  def y(self) :
    """ a vector containing the equation  """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "outputVector(O)")
    return vec

  def x(self) :
    """ a vector containing the x vector  """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "outputVector(XO)")
    return vec

  def set_x(self, xvector): 
    self.client.send_si(self.handle, "setInputVector(X,"+xvector.handle+")")

# Histogram ############################################################
class Histogram(Object) : 
  """ A Histogram inside kst.
                          
    :param vector: the vector to take the histogram of
    :param bin_min: the low end of the lowest bin
    :param bin_max: the high end of the highest bin
    :param num_bins: the number of bins
    :param normalization: see below
    :param auto_bin: if True, set xmin and xmax based on the vector
    
    The normalization types are::
    
     0: Number in the bin     1: Percent in the bin
     2: Fraction in the bin   3: Peak is normalized to 1.0
    
  """
  def __init__(self, client, vector, bin_min, bin_max, num_bins, 
               normalization = 0, auto_bin = False, 
               name="", new=True) :
    Object.__init__(self,client)
    
    if (new == True):      
      self.client.send("newHistogram()")

      self.client.send("change(" + vector.handle + "," +
                       b2str(bin_min) + "," +
                       b2str(bin_max) + "," +
                       b2str(num_bins) + "," +
                       b2str(normalization) + "," +
                       b2str(auto_bin) + ")")

      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)
      self.set_name(name)
    else:
      self.handle = name

  def y(self) :
    """ a vector containing the histogram values  """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "outputVector(H)")
    return vec

  def x(self) :
    """ a vector containing the bin centers  """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "outputVector(B)")
    return vec

  def change(self, vector, bin_min, bin_max, num_bins, 
             normalization = 0, auto_bin = False):
    """ Change Histogram parameters.
    
    :param vector: the vector to take the histogram of
    :param bin_min: the low end of the lowest bin
    :param bin_max: the high end of the highest bin
    :param num_bins: the number of bins
    :param normalization: See :class:`Histogram`
    :param auto_bin: if True, set xmin and xmax based on the vector

    """
    self.client.send_si(self.handle, "change(" +
                        vector.handle + "," +
                        b2str(bin_min) + "," +
                        b2str(bin_max) + "," +
                        b2str(num_bins) + "," +
                        b2str(normalization) + "," +
                        b2str(auto_bin) + ")")

  def bin_min(self):
    """ the low end of the lowest bin """
    retval = self.client.send_si(self.handle, "xMin()")
    return retval

  def bin_max(self):
    """ the high end of the lowest bin """
    retval = self.client.send_si(self.handle, "xMax()")
    return retval

  def num_bins(self):
    """ the number of bins """
    retval = self.client.send_si(self.handle, "nBins()")
    return retval

  def normalization(self):
    """ how the bins are normalized 
    
    See :class:`Histogram`
    
    """
    retval = self.client.send_si(self.handle, "normalizationType()")
    return retval

  def auto_bin(self):
    """ if True, xmin and xmax are set based on the vector """
    retval = self.client.send_si(self.handle, "autoBin()")
    return retval

# Spectrum ############################################################
class Spectrum(Object) : 
  """ An spectrum inside kst.
   
    :param vector: the vector to take the spectrum of
    :param sample_rate: the sample rate of the vector
    :param interleaved_average: average spectra of length fft_length
    :param fft_length: the fft is 2^fft_length long if interleaved_average is true.
    :param apodize: if true, apodize the vector first
    :param remove_mean: if true, remove mean first
    :param vector_unints: units of the input vector - for labels.
    :param rate_units: the units of the sample rate - for labels.
    :param apodize_function: index of the apodization function - see apodize_function()
    :param sigma: only used if gausian apodization is selected.
    :param output_type: index for the output type - see output_type()

    The apodize funcition is::
    
     0: default          1: Bartlett
     2: Window           3: Connes
     4: Cosine           5: Gaussian
     6: Hamming          7: Hann
     8: Welch            9: Uniform
    
    The output type is::
    
     0: Amplitude Spectral Density  1: Power Spectral Density
     2: AmplitudeSpectrum           3: Power Spectrum
    
    
  """
  def __init__(self, client, 
               vector, 
               sample_rate = 1.0, 
               interleaved_average = False,
               fft_length = 10,
               apodize = True, 
               remove_mean = True, 
               vector_units = "",
               rate_units = "Hz",
               apodize_function = 0,
               sigma = 1.0,
               output_type = 0,
               name="", new=True) :
    
    Object.__init__(self,client)
    
    if (new == True):      
      self.client.send("newSpectrum()")

      self.client.send("change(" + vector.handle + "," +
                       b2str(sample_rate) + "," +
                       b2str(interleaved_average) + "," +
                       b2str(fft_length) + "," +
                       b2str(apodize) + "," +
                       b2str(remove_mean) + "," +
                       vector_units + "," +
                       rate_units + "," +
                       b2str(apodize_function) + "," +
                       b2str(sigma) + "," +
                       b2str(output_type) + "," + ")")

      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)
      self.set_name(name)
    else:
      self.handle = name

  def y(self) :
    """ a vector containing the spectrum  """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "outputVector(S)")
    return vec

  def x(self) :
    """ a vector containing the frequency bins  """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "outputVector(F)")
    return vec

  def set_vector(self, xvector): 
    """ set the input vector """
    self.client.send_si(self.handle, "setInputVector(I,"+xvector.handle+")")

  def interleaved_average(self):
    """ average spectra of length fft_length() """
    retval = self.client.send_si(self.handle, "interleavedAverage()")
    return retval

  def sample_rate(self):
    """ the sample rate assumed for the spectra. """
    retval = self.client.send_si(self.handle, "sampleRate()")
    return retval

  def fft_length(self):
    """ ffts are 2^fft_length() long if interleaved_average is set """
    retval = self.client.send_si(self.handle, "fftLength()")
    return retval

  def apodize(self):
    """ apodize before taking spectra, if set """
    retval = self.client.send_si(self.handle, "apodize()")
    return retval

  def remove_mean(self):
    """ remove mean before taking spectra, if set """
    retval = self.client.send_si(self.handle, "removeMean()")
    return retval

  def vector_units(self):
    """ the units of the input vector.  For labels """
    retval = self.client.send_si(self.handle, "vectorUnits()")
    return retval

  def rate_units(self):
    """ the units of the sample rate.  For labels """
    retval = self.client.send_si(self.handle, "rateUnits()")
    return retval

  def apodize_function(self):
    """ the index of the apodize function.
    
    The apodize funcition is::
    
     0: default          1: Bartlett
     2: Window           3: Connes
     4: Cosine           5: Gaussian
     6: Hamming          7: Hann
     8: Welch            9: Uniform
    
    """
    retval = self.client.send_si(self.handle, "apodizeFunctionIndex()")
    return retval

  def gaussian_sigma(self):
    """ the width, if apodize_funcion_index() is 5 (gaussian). """
    retval = self.client.send_si(self.handle, "gaussianSigma()")
    return retval

  def output_type(self):
    """ the index of the spectrum output type.
    
    The output type is::
    
     0: Amplitude Spectral Density  1: Power Spectral Density
     2: AmplitudeSpectrum           3: Power Spectrum
    
    """

    retval = self.client.send_si(self.handle, "outputTypeIndex()")
    return retval


# FILTER ################################################################
class Filter(Object) :
  """ This is a class which provides some methods common to all filters """
  def __init__(self,client) :
    Object.__init__(self,client)

  def output(self) :
    """ a vector containing the output of the filter  """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "outputVector(Y)")
    return vec

# FLAG FILTER ############################################################
class FlagFilter(Filter) :
  """ a flagged vector inside kst

  The output is the input when flag == 0, or NaN if flag is non-0.
  """
  def __init__(self, client, yvector, flag, name="", new=True) :
    Filter.__init__(self,client)

    if (new == True):
      self.client.send("newPlugin(Flag Filter)")

      self.client.send("setInputVector(Y Vector,"+yvector.handle+")")
      self.client.send("setInputVector(Flag Vector,"+flag.handle+")")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)
      self.set_name(name)
    else:
      self.handle = name


# FIT ###################################################################
class Fit(Object) :
  """ This is a class which provides some methods common to all fits """
  def __init__(self,client) :
    Object.__init__(self,client)

  def parameters(self) :
    """ a vector containing the Parameters of the fit  """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "outputVector(Parameters Vector)")
    return vec

  def fit(self) :
    """ a vector containing the fit  """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "outputVector(Fit)")
    return vec

  def residuals(self) :
    """ a vector containing the Parameters of the fit  """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "outputVector(Residuals)")
    return vec

  def covariance(self) :
    """ a vector containing the Covariance of the fit  """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "outputVector(Covariance)")
    return vec

  def reduced_chi2(self) :
    """ a scalar containing the Parameters of the fit  """
    X = Scalar(self.client)
    X.handle = self.client.send_si(self.handle, "outputScalar(chi^2/nu)")
    return X


# LINEAR FIT ############################################################
class LinearFit(Fit) : 
  """ A linear fit inside kst.
   
  If weightvector is 0, then the fit is unweighted.   
  """
  def __init__(self, client, xvector, yvector, weightvector=0, name="", new=True) :
    Fit.__init__(self,client)
    
    if (new == True):      
      if weightvector==0:
        self.client.send("newPlugin(Linear Fit)")
      else:
        self.client.send("newPlugin(Linear Weighted Fit)")
        self.client.send("setInputVector(Weights Vector,"+weightvector.handle+")")
          
      self.client.send("setInputVector(X Vector,"+xvector.handle+")")
      self.client.send("setInputVector(Y Vector,"+yvector.handle+")")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)
      self.set_name(name)
    else:
      self.handle = name

  def slope(self) :
    """ The slope of the fit.  """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "outputVector(Parameters Vector)")
    return vec.value(1)

  def intercept(self) :
    """ The intercept of the fit.  """
    vec = VectorBase(self.client)
    vec.handle = self.client.send_si(self.handle, "outputVector(Parameters Vector)")
    return vec.value(0)

# POLYNOMIAL FIT ############################################################
class PolynomialFit(Fit) : 
  """ A Polynomial fit inside kst.

     :param order: The order of the fit
  """
  def __init__(self, client, order, xvector, yvector, weightvector=0, name="", new=True) :
    Fit.__init__(self,client)
    
    if (new == True):      
      if weightvector==0:
        self.client.send("newPlugin(Polynomial Fit)")
      else:
        self.client.send("newPlugin(Polynomial Weighted Fit)")
        self.client.send("setInputVector(Weights Vector,"+weightvector.handle+")")
          
      self.client.send("setInputVector(X Vector,"+xvector.handle+")")
      self.client.send("setInputVector(Y Vector,"+yvector.handle+")")
      self.client.send("setInputScalar(Order Scalar,"+order.handle+")")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)
      self.set_name(name)
    else:
      self.handle = name



# View Items ################################################################
class ViewItem(NamedObject):
  """ Convenience class. You should not use it directly."""
  def __init__(self,client):
    self.client=client
    
  def set_h_margin(self,margin):
    self.client.send_si(self.handle, 
                        "setLayoutHorizontalMargin("+b2str(margin)+")")

  def set_v_margin(self,margin):
    self.client.send_si(self.handle, 
                        "setLayoutVerticalMargin("+b2str(margin)+")")

  def set_h_space(self,space):
    self.client.send_si(self.handle, 
                        "setLayoutHorizontalSpacing("+b2str(space)+")")

  def set_v_space(self,space):
    self.client.send_si(self.handle, 
                        "setLayoutVerticalSpacing("+b2str(space)+")")

  def set_fill_color(self,color):
    """ Set the fill/background color.
    
    Colors are given by a name such as ``red`` or a hex number such 
    as ``#FF0000``. 

    """
    self.client.send_si(self.handle, b2str("setFillColor("+b2str(color)+")"))
    
  def set_fill_style(self,style):
    """ Set the background fill style.
    
    This is equivalent to setting the index of Apperance>Fill>Style within 
    a view item dialog in kst.::
    
     0:  NoBrush          1:  SolidPattern
     2:  Dense1Pattern    3:  Dense2Pattern
     4:  Dense3Pattern    5:  Dense4Pattern
     6:  Dense5Pattern    7:  Dense6Pattern
     8:  Dense7Pattern    9:  HorPattern
     11: VerPattern       12: CrossPattern, 
     13: BDiagPattern     14: FDiagPattern.
    
    """
    self.client.send_si(self.handle, 
                        "setIndexOfFillStyle("+b2str(style)+")")

  def set_stroke_style(self,style):
    """ Set the stroke style of lines for the item.
    
    This is equivalent to setting the index of Apperance>Stroke>Style 
    within a view item dialog in kst::
    
     0: SolidLine       1: DashLine
     2: DotLine         3: DashDotLine 
     4: DashDotDotLine  5: CustomDashLine
     
    """
    self.client.send_si(self.handle, "setIndexOfStrokeStyle("+b2str(style)+")")

  def set_stroke_width(self,width):
    """ Set the width of lines for the item. """
    self.client.send_si(self.handle, "setStrokeWidth("+b2str(width)+")")

  def set_stroke_brush_color(self,color):
    """ Set the color for lines for the item.
    
    Colors are given by a name such as ``red`` or a hex number 
    such as ``#FF0000``. 
    """
    self.client.send_si(self.handle, "setStrokeBrushColor("+b2str(color)+")")

  def set_stroke_brush_style(self,style):
    """ Set the brush style for lines for the item.
    
    This is equivalent to setting the index of Apperance>Stroke>Brush Style 
    within a view item dialog in kst.  
    
    This sets the brush type for lines in the item, and not for the fill, 
    so values other than ``1`` (SolidPattern) only make sense for wide lines
    and are rarely used::
    
     0:  NoBrush          1:  SolidPattern
     2:  Dense1Pattern    3:  Dense2Pattern
     4:  Dense3Pattern    5:  Dense4Pattern
     6:  Dense5Pattern    7:  Dense6Pattern
     8:  Dense7Pattern    9:  HorPattern
     11: VerPattern       12: CrossPattern, 
     13: BDiagPattern     14: FDiagPattern.
    
    """
    self.client.send_si(self.handle, 
                        "setIndexOfStrokeBrushStyle("+b2str(style)+")")

  def set_stroke_join_style(self,style):
    """ Set the style by which lines are joined in the item.
    
    This is equivalent to setting the index of Apperance>Stroke>Join Style 
    within a view item dialog in kst.
    
    0 is MiterJoin, 1 is BevelJoin, 2 is RoundJoin,
    and 3 is SvgMiterJoin.
    """
    self.client.send_si(self.handle, 
                        "setIndexOfStrokeJoinStyle("+b2str(style)+")")

  def set_stroke_cap_style(self,style):
    """ Set the cap style for the ends of lines in the item.
    
    This is equivalent to setting the index of Apperance>Stroke>Cap Style 
    within a view item dialog in kst.
    
    0 is FlatCap, 1 is SquareCap, and 2 is RoundCap.
    """
    self.client.send_si(self.handle, 
                        "setIndexOfStrokeCapStyle("+b2str(style)+")")

  def set_fixed_aspect_ratio(self, fixed=True):
    """ if True, fix the aspect ratio of the item to its current value.
    
    This is equivalent to checking Dimensions>Fix aspect ratio within a 
    view item dialog in kst.
    """
    if fixed == True:
      self.client.send_si(self.handle, b2str("checkFixAspectRatio()"))
    else:
      self.client.send_si(self.handle, b2str("uncheckFixAspectRatio()"))

  def set_pos(self,pos):
    """ Set the center position of the item.
    
    :param pos: a 2 element tuple ``(x,y)`` specifying the position.  The Top Left is (0,0).
                The Bottom Right is (1,1)

    This is equivalent to setting Dimensions>Position within a view 
    item dialog in kst.    
    """
    x,y = pos
    
    self.client.send("beginEdit("+self.handle+")")
    self.client.send("setPosX("+b2str(x)+")")
    self.client.send("setPosY("+b2str(y)+")")
    self.client.send("endEdit()")

  def set_size(self,size):
    """ Set the size of the item.
    
    :param size: a 2 element tuple ``(w,h)`` specifying the size.

    Elements go from 0 to 1.  If the aspect ratio is fixed, then ``h`` 
    is ignored.

    This is equivalent to setting Dimensions>Position within a view 
    item dialog in kst.    
    
    """
    w,h = size
    self.client.send("beginEdit("+self.handle+")")
    self.client.send("setGeoX("+b2str(w)+")")
    self.client.send("setGeoY("+b2str(h)+")")
    self.client.send("endEdit()")

  def set_rotation(self,rot):
    """ Set the rotation of the item.
    
    This is equivalent to setting Dimensions>Rotation within a view item dialog.
    
    """
    self.client.send_si(self.handle, b2str("setRotation("+b2str(rot)+")"))

  def remove(self):
    """ This removes the object from Kst. """
    self.client.send("eliminate("+self.handle+")")


# LABELS ######################################################################
class Label(ViewItem) :
  """ A floating label inside kst.

  :param text: the text of the label.  Supports scalars, equations, and a 
               LaTeX subset.
  :param pos: a 2 element tuple ``(x,y)`` specifying the position. 
              (0,0) is top left.  (1,1) is bottom right.
  :param rot: rotation of the label in degrees.
  :param font_size: size of the label in points, when the printed at the
                   reference size.
  :param font_color: Colors are given by a name such as ``red`` or a 
                    hex number such as ``#FF0000``. 
  :param font_family: The font family.  eg, TimeNewRoman.
  
  Scalars and scalar equations can be displayed live in labels. 
  When the scalar is updated, the label is updated.
  
  The format is::
    Scalar:         [scalarname]         eg [GYRO1:Mean(X4)]
    Vector Element: [vectorName[index]]  eg [GYRO1 (V2)[4]]
    Equation:       [=equation]          eg [=[GYRO1:Mean(X4)]/[GYRO1:Sigma (X4)]]
    
  Labels in kst support a derrivitive subset of LaTeX. For example, to display 
  the equation for the area of a circle, you could set the label to ``A=2\pir^2``. 
  Unlike LaTeX, it is not necessary to enter math mode using ``$``. Also, 
  unlike LaTeX, variables are not automatically displayed in italic font. 
  If desired, this must be done explicitly using ``\\textit{}``. 
  
  Greek letters: \\\\name or \\\\Name. eg: ``\\alpha``
  
  Other symbols: ``\\approx, \\cdot, \\ge, \\geq, \\inf, \\approx, \\cdot, 
  \\ge, \\geq, \\inf, \\int, \\le, \\leq, \\ne, \\n, \\partial, \\prod, \\pm, 
  \\sum, \\sqrt``
  
  Font effects: ``\\textcolor{colorname}{colored text}, \\textbf{bold text},
  \\textit{italicized text}, \\underline{underlined text}, 
  \\overline{overlined text}.``
  
  Other:``x^y``, ``x_y``, ``\\t``, ``\\n``, ``\\[``

  This class represents a label you would create via "Create>Annotations>Label" 
  from the menubar inside kst.  
  
  Use the convenience function in Client to create a label "Test Label" in kst::
  
    import pykst as kst
    client = kst.Client()
    L = client.new_label("Test Label", (0.25, 0.25), font_size=18)

  """
  def __init__(self,client, text, pos=(0.5,0.5), rot=0, font_size=12, 
               bold=False, italic=False, font_color="black", 
               font_family="Serif", name="", new=True) :
    ViewItem.__init__(self,client)

    if (new == True):
      self.client.send("newLabel()")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)

      self.set_text(text)
      self.set_label_font_size(font_size)
      self.set_pos(pos)
      self.set_fixed_aspect_ratio(True)
      self.set_rotation(rot)
      self.set_font_color(font_color)
      self.set_font_family(font_family)

      self.set_font_bold(bold)
      self.set_font_italic(italic)
      self.set_name(name)
    else:
      self.handle = name      

  def set_text(self,text):
    """ Set text displayed by the label. 

    Scalars and scalar equations can be displayed live in labels. 
    When the scalar is updated, the label is updated.
    The format is::
    
      Scalar:         [scalarname]         eg [GYRO1:Mean(X4)]
      Vector Element: [vectorName[index]]  eg [GYRO1 (V2)[4]]
      Equation:       [=equation]          eg [=[GYRO1:Mean(X4)]/[GYRO1:Sigma (X4)]]
    
    Labels in kst support a derrivitive subset of LaTeX. For example, 
    to display the equation for the area of a circle, you could set the 
    label to ``A=2\pir^2``. Unlike LaTeX, it is not necessary to enter
    math mode using ``$``. Also, unlike LaTeX, variables are not 
    automatically displayed in italic font.  If desired, this must be done 
    explicitly using ``\\textit{}``. 
    
    Greek letters: \\\\name or \\\\Name. eg: ``\\alpha``
    
    Other symbols: ``\\approx, \\cdot, \\ge, \\geq, \\inf, \\approx, \\cdot, 
    \\ge, \\geq, \\inf, \\int, \\le, \\leq, \\ne, \\n, \\partial, \\prod, \\pm, 
    \\sum, \\sqrt``
    
    Font effects: ``\\textcolor{colorname}{colored text}, \\textbf{bold text},
    \\textit{italicized text}, \\underline{underlined text}, 
    \\overline{overlined text}.``
    
    Other:``x^y``, ``x_y``, ``\\t``, ``\\n``, ``\\[``    
    """
    self.client.send_si(self.handle, b2str("setLabel("+b2str(text)+")"))

  def set_label_font_size(self,size):
    """ size of the label in points, when the printed at the reference size."""
    self.client.send_si(self.handle, b2str("setFontSize("+b2str(size)+")"))

  def set_font_bold(self, bold = True):
    """ . . . """
    if bold == True:
      self.client.send_si(self.handle, b2str("checkLabelBold()"))
    else:
      self.client.send_si(self.handle, b2str("uncheckLabelBold()"))

  def set_font_italic(self, italic = True):
    """ . . . """
    if italic == True:
      self.client.send_si(self.handle, b2str("checkLabelItalic()"))
    else:
      self.client.send_si(self.handle, b2str("uncheckLabelItalic()"))

  def set_font_color(self,color):
    """ Colors are given by a name such as ``red`` or a hex number such 
    as ``#FF0000`` """
    self.client.send_si(self.handle, b2str("setLabelColor("+b2str(color)+")"))

  def set_font_family(self,family):
    """ set the font family.  eg, TimeNewRoman. """
    self.client.send_si(self.handle, b2str("setFontFamily("+b2str(family)+")"))


class ExistingLabel(Label):
  def  __init__(self,client,handle):
    ViewItem.__init__(self,client)
    self.handle=handle
    
  @classmethod
  def getList(cls,client):
    x=client.send("getLabelList()")
    ret=[]
    while x.contains('['):
      y=x
      y.remove(0,1)
      y.remove(y.indexOf(']'),9999999)
      x.remove(0,x.indexOf(']')+1)
      ret.append(ExistingLabel(client,y))
    return ret
  

class Legend(ViewItem) :
  """ A legend in a plot in kst.

  : param plot: a plot in kst.
  Use the convenience function in Client to create a legend in kst::

    import pykst as kst
    client = kst.Client()
   ...
    P1 = client.new_plot()
    L1 = client.new_legend(P1)

  """
  def __init__(self,client, plot, name="", new=True) :
    ViewItem.__init__(self,client)

    if (new == True):
      self.client.send("newLegend("+plot.name()+")")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)
    else:
      self.handle = name

  def set_font_size(self,size):
    """ size of the label in points, when the printed at the reference size."""
    self.client.send_si(self.handle, b2str("setFontSize("+b2str(size)+")"))

  def set_font_bold(self, bold = True):
    """ . . . """
    if bold == True:
      self.client.send_si(self.handle, b2str("checkLabelBold()"))
    else:
      self.client.send_si(self.handle, b2str("uncheckLabelBold()"))

  def set_font_italic(self, italic = True):
    """ . . . """
    if italic == True:
      self.client.send_si(self.handle, b2str("checkLabelItalic()"))
    else:
      self.client.send_si(self.handle, b2str("uncheckLabelItalic()"))

  def set_font_color(self,color):
    """ Colors are given by a name such as ``red`` or a hex number such
    as ``#FF0000`` """
    self.client.send_si(self.handle, b2str("setLegendColor("+b2str(color)+")"))

  def set_font_family(self,family):
    """ set the font family.  eg, TimeNewRoman. """
    self.client.send_si(self.handle, b2str("setFontFamily("+b2str(family)+")"))


class Box(ViewItem) :
  """ A floating box inside kst.

  :param pos: a 2 element tuple ``(x,y)`` specifying the position. 
              ``(0,0)`` is top left.  ``(1,1)`` is bottom right.
  :param size: a 2 element tuple ``(w,h)`` specifying the size.
              ``(1,1)`` is the size of the window.
  :param rotation: rotation of the label in degrees.
  :param fill_color: the background color.
  :param fill_style: the background fill style.  See set_fill_style.
  :param stroke_style: see set_stroke_style
  :param stroke_width: the pen width for the box outline.
  :param stroke_brush_color: the box outline color
  :param stroke_brush_style: see set_stroke_brush_style
  :param strokeJoinStyle: see set_stroke_join_style
  :param stroke_cap_style: see set_stroke_cap_style
  :param fix_aspect: if true, the box will have a fixed aspect ratio.

  Colors are given by a name such as ``red`` or a hex number such 
  as ``#FF0000``. 
  
  This class represents a box you would create via "Create>Annotations>Box" 
  from the menubar inside kst.
  
  Use the convenience function in Client to create a box in kst::
  
    import pykst as kst
    client = kst.Client()
    ...
    B = client.new_box((0.25, 0.25), (0.2, 0.1), fill_color="blue")
  
  """
  def __init__(self,client, pos=(0.1,0.1), size=(0.1,0.1), rot=0, 
               fill_color="white", fill_style=1, stroke_style=1, stroke_width=1,
               stroke_brush_color="black", stroke_brush_style=1, 
               strokeJoinStyle=1, stroke_cap_style=1, fix_aspect=False,
               name="", new=True) :
    ViewItem.__init__(self,client)

    if (new == True):
      self.client.send("newBox()")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)

      self.set_pos(pos)
      self.set_size(size)

      self.set_fixed_aspect_ratio(fix_aspect)
      self.set_rotation(rot)

      self.set_stroke_brush_color(stroke_brush_color)
      self.set_fill_color(fill_color)
      self.set_fill_style(fill_style)
      self.set_stroke_style(stroke_style)
      self.set_stroke_width(stroke_width)
      self.set_stroke_brush_color(stroke_brush_color)
      self.set_stroke_brush_style(stroke_brush_style)
      self.set_stroke_join_style(strokeJoinStyle)
      self.set_stroke_cap_style(stroke_cap_style)
      self.set_name(name)
    else:
      self.handle = name      

  @classmethod
  def getList(cls,client):
    x=client.send("getBoxList()")
    ret=[]
    while x.contains('['):
      y=x
      y.remove(0,1)
      y.remove(y.indexOf(']'),9999999)
      x.remove(0,x.indexOf(']')+1)
      ret.append(ExistingViewItem(client,y))
    return ret





class Circle(ViewItem) :
  """ A floating circle inside kst.

  :param pos: a 2 element tuple ``(x,y)`` specifying the position. 
              ``(0,0)`` is top left.  ``(1,1)`` is bottom right.
  :param diameter: the diameter of the circle.  1 is the width of the window.
  :param fill_color: the background color.
  :param fill_style: the background fill style.  See set_fill_style.
  :param stroke_style: see set_stroke_style
  :param stroke_width: the pen width for the circle outline.
  :param stroke_brush_color: the circle outline color
  :param stroke_brush_style: see set_stroke_brush_style
  
  Colors are given by a name such as ``red`` or a hex number such 
  as ``#FF0000``. 
  
  This class represents a circle you would create via 
  "Create>Annotations>Circle" from the menubar inside kst.

  Use the convenience function in Client to create a circle in kst::
  
    import pykst as kst
    client = kst.Client()
    ...
    Cr = client.new_circle((0.5, 0.5), 0.2, fill_color="red")
  
  """
  def __init__(self,client,pos=(0.1, 0.1), diameter=0.1,
               fill_color="white",fill_style=1,stroke_style=1,
               stroke_width=1,stroke_brush_color="grey",stroke_brush_style=1, 
               name="", new=True) :
    ViewItem.__init__(self,client)

    if (new == True):
      self.client.send("newCircle()")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)

      self.set_pos(pos)
      self.set_diameter(diameter)

      self.set_stroke_brush_color(stroke_brush_color)
      self.set_fill_color(fill_color)
      self.set_fill_style(fill_style)
      self.set_stroke_style(stroke_style)
      self.set_stroke_width(stroke_width)
      self.set_stroke_brush_color(stroke_brush_color)
      self.set_stroke_brush_style(stroke_brush_style)
      self.set_name(name)
    else:
      self.handle = name      

  @classmethod
  def getList(cls,client):
    x=client.send("getCircleList()")
    ret=[]
    while x.contains('['):
      y=x
      y.remove(0,1)
      y.remove(y.indexOf(']'),9999999)
      x.remove(0,x.indexOf(']')+1)
      ret.append(ExistingViewItem(client,y))
    return ret
    
  def set_diameter(self,diameter):
    """ set the diamter of the circle.
    
    The width of the window is 1.0.
    """
    self.client.send_si(self.handle,"setGeoX("+b2str(diameter)+")")


class Ellipse(ViewItem) :
  """ A floating ellipse inside kst.

  :param pos: a 2 element tuple ``(x,y)`` specifying the position. 
              ``(0,0)`` is top left.  ``(1,1)`` is bottom right.
  :param size: a 2 element tuple ``(w,h)`` specifying the size.
              ``(1,1)`` is the size of the window.
  :param fill_color: the background color.
  :param fill_style: the background fill style.  See set_fill_style.
  :param stroke_style: see set_stroke_style
  :param stroke_width: the pen width for the ellipse outline.
  :param stroke_brush_color: the ellipse outline color
  :param stroke_brush_style: see set_stroke_brush_style
  
  Colors are given by a name such as ``red`` or a hex number such 
  as ``#FF0000``. 
  
  This class represents an ellipse you would create via 
  "Create>Annotations>Ellipse" from the menubar inside kst.

  Use the convenience function in Client to create an Ellipse in kst::
  
    import pykst as kst
    client = kst.Client()
    ...
    E = client.new_ellipse((0.25, 0.25), (0.2, 0.1), fill_color="green")
  
  """
  def __init__(self,client,pos=(0.1,0.1), size=(0.1,0.1),
               rot=0, fill_color="white", fill_style=1, stroke_style=1,
               stroke_width=1, stroke_brush_color="black", stroke_brush_style=1,
               fix_aspect=False, name="", new=True) :
    ViewItem.__init__(self,client)

    if (new == True):
      self.client.send("newEllipse()")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)

      self.set_pos(pos)
      self.set_size(size)
      if fix_aspect==True:
          self.set_fixed_aspect_ratio(True)
      else:
          self.set_fixed_aspect_ratio(False)

      self.set_rotation(rot)

      self.set_stroke_brush_color(stroke_brush_color)
      self.set_fill_color(fill_color)
      self.set_fill_style(fill_style)
      self.set_stroke_style(stroke_style)
      self.set_stroke_width(stroke_width)
      self.set_stroke_brush_color(stroke_brush_color)
      self.set_stroke_brush_style(stroke_brush_style)
      self.set_name(name)
    else:
      self.handle = name      

  @classmethod
  def getList(cls,client):
    x=client.send("getEllipseList()")
    ret=[]
    while x.contains('['):
      y=x
      y.remove(0,1)
      y.remove(y.indexOf(']'),9999999)
      x.remove(0,x.indexOf(']')+1)
      ret.append(ExistingViewItem(client,y))
    return ret





class Line(ViewItem) :
  """ A floating line inside kst.

  :param pos: a 2 element tuple ``(x,y)`` specifying the position of the
              center of the line. 
              ``(0,0)`` is top left.  ``(1,1)`` is bottom right.
  :param length: The length of the line.  1 is the width of the window.
  :param rot: rotation of the line in degrees.
  :param stroke_style: see set_stroke_style
  :param stroke_width: the pen width for the ellipse outline.
  :param stroke_brush_color: the ellipse outline color
  :param stroke_brush_style: see set_stroke_brush_style
  :param stroke_cap_style: see set_stroke_cap_style

  Colors are given by a name such as ``red`` or a hex number such 
  as ``#FF0000``. 
  
  This class represents a line you would create via "Create>Annotations>Line" from the menubar inside kst.

  Colors are given by a name such as ``red`` or a hex number such as ``#FF0000``".
  
  Use the convenience function in Client to create a line in kst::
  
    import pykst as kst
    client = kst.Client()
    ...
    Ln = client.new_line((0.25, 0.25), 0.2, rot=15)

  """
  def __init__(self,client,pos=(0.1,0.1),length=0.1,rot=0,
               stroke_style=1,stroke_width=1,stroke_brush_color="black",
               stroke_brush_style=1,stroke_cap_style=1, name="", new=True) :
    ViewItem.__init__(self,client)

    if (new == True):
      self.client.send("newLine()")
      self.handle=self.client.send("endEdit()")

      self.handle.remove(0,self.handle.indexOf("ing ")+4)

      self.set_pos(pos)
      self.set_length(length)
      self.set_rotation(rot)

      self.set_stroke_brush_color(stroke_brush_color)
      self.set_stroke_style(stroke_style)
      self.set_stroke_width(stroke_width)
      self.set_stroke_brush_color(stroke_brush_color)
      self.set_stroke_brush_style(stroke_brush_style)
      self.set_stroke_cap_style(stroke_cap_style)
      self.set_name(name)
    else:
      self.handle = name      

  @classmethod
  def getList(cls,client):
    x=client.send("getLineList()")
    ret=[]
    while x.contains('['):
      y=x
      y.remove(0,1)
      y.remove(y.indexOf(']'),9999999)
      x.remove(0,x.indexOf(']')+1)
      ret.append(ExistingViewItem(client,y))
    return ret

  def set_length(self, length):
    """ set the length of the line.
    
    The width of the window is 1.0.
    """
    self.client.send_si(self.handle,"setGeoX("+b2str(length)+")")


class Arrow(ViewItem) :
  """ A floating arrow inside kst.

  :param pos: a 2 element tuple ``(x,y)`` specifying the position of the
              center of the line. 
              ``(0,0)`` is top left.  ``(1,1)`` is bottom right.
  :param length: The length of the line.  1 is the width of the window.
  :param rot: rotation of the line in degrees.
  :param arror_at_start: if True, draw an arrow at the start of the line.
  :param arrow_at_end: if True, draw an arrow at the end of the line.
  :param arrow_size: the size of the arrow.
  :param stroke_style: see set_stroke_style.
  :param stroke_width: the pen width for the ellipse outline.
  :param stroke_brush_color: the ellipse outline color
  :param stroke_brush_style: see set_stroke_brush_style
  :param stroke_cap_style: see set_stroke_cap_style

  Colors are given by a name such as ``red`` or a hex number such 
  as ``#FF0000``. 
  
  This class represents an arrow you would create via 
  "Create>Annotations>Arrow" from the menubar inside kst.

  Use the convenience function in Client to create an arrow in kst::
  
    import pykst as kst
    client = kst.Client()
    ...
    Ln = client.new_arrow((0.25, 0.25), 0.2, rot=15, arror_at_start=True)
    
  """
  def __init__(self,client,pos=(0.1,0.1), length=0.1, rot=0, 
               arror_at_start = False, arrow_at_end = True, arrow_size = 12.0, 
               stroke_style=1, stroke_width=1, stroke_brush_color="black",
               stroke_brush_style=1, stroke_cap_style=1, name="", new=True) :
    ViewItem.__init__(self,client)

    if (new == True):
      self.client.send("newArrow()")
      self.handle=self.client.send("endEdit()")
      self.handle.remove(0,self.handle.indexOf("ing ")+4)

      self.set_pos(pos)
      self.set_length(length)
      self.set_rotation(rot)

      self.set_stroke_brush_color(stroke_brush_color)
      self.set_stroke_style(stroke_style)
      self.set_stroke_width(stroke_width)
      self.set_stroke_brush_color(stroke_brush_color)
      self.set_stroke_brush_style(stroke_brush_style)
      self.set_stroke_cap_style(stroke_cap_style)
      self.set_arrow_at_start(arror_at_start)
      self.set_arrow_at_end(arrow_at_end)
      self.set_arrow_size(arrow_size)
      self.set_name(name)
    else:
      self.handle = name      

  def set_arrow_at_start(self, arrow=True) :
    """ Set whether an arrow head is shown at the start of the line """
    if arrow==True:
      self.client.send_si(self.handle, b2str("arrowAtStart(True)"))
    else:
      self.client.send_si(self.handle, b2str("arrowAtStart(False)"))

  def set_arrow_at_end(self, arrow=True) :
    """ Set whether an arrow head is shown at the end of the line """
    if arrow==True:
      self.client.send_si(self.handle, b2str("arrowAtEnd(True)"))
    else:
      self.client.send_si(self.handle, b2str("arrowAtEnd(False)"))

  def set_arrow_size(self, arrow_size) :
    self.client.send_si(self.handle, b2str("arrowHeadScale("+b2str(arrow_size)+")"))

  def set_length(self, length):
    """ set the length of the line.
    
    The width of the window is 1.0.
    """
    self.client.send_si(self.handle,"setGeoX("+b2str(length)+")")

  @classmethod
  def getList(cls,client):
    x=client.send("getArrowList()")
    ret=[]
    while x.contains('['):
      y=x
      y.remove(0,1)
      y.remove(y.indexOf(']'),9999999)
      x.remove(0,x.indexOf(']')+1)
      ret.append(ExistingViewItem(client,y))
    return ret
    
    
    
    
class Picture(ViewItem) :
  """ A floating image inside kst.

  :param filename: the file which holds the image to be shown.
  :param pos: a 2 element tuple ``(x,y)`` specifying the position of the
              center of the picture. 
              ``(0,0)`` is top left.  ``(1,1)`` is bottom right.
  :param width: The width of the picture.  1 is the width of the window.
  :param rot: rotation of the picture in degrees.

  This class represents a picture you would create via 
  "Create>Annotations>Picture" from the menubar inside kst.
  
  Use the convenience function in Client to create a picture in kst::
  
    import pykst as kst
    client = kst.Client()
    ...
    pic = client.new_picture("image.jpg", (0.25, 0.25), 0.2)

  BUG: the aspect ratio of the picture is wrong.
  """
  def __init__(self,client,filename,pos=(0.1,0.1), width=0.1,rot=0, 
               name="", new=True) :
    ViewItem.__init__(self,client)

    if (new == True):
      self.client.send("newPicture("+b2str(filename)+")")
      self.handle=self.client.send("endEdit()")

      self.handle.remove(0,self.handle.indexOf("ing ")+4)

      self.set_pos(pos)
      self.set_width(width)
      self.set_fixed_aspect_ratio(True)
      self.set_rotation(rot)
      self.set_name(name)
    else:
      self.handle = name      

  def set_width(self, width):
    """ set the width of the picture.
    
    The width of the window is 1.0.
    """
    self.client.send_si(self.handle,"setGeoX("+b2str(width)+")")
  

  def set_picture(self,pic):
    """ BUG: aspect ratio is not changed. There is no parellel for this 
    function within the kst GUI. """
    self.client.send_si(self.handle, b2str("setPicture("+b2str(pic)+")"))
    
  @classmethod
  def getList(cls,client):
    x=client.send("getPictureList()")
    ret=[]
    while x.contains('['):
      y=x
      y.remove(0,1)
      y.remove(y.indexOf(']'),9999999)
      x.remove(0,x.indexOf(']')+1)
      ret.append(ExistingPicture(client,y))
    return ret





class SVG(ViewItem) :
  """ A floating svg image inside kst.

  :param filename: the file which holds the svg image to be shown.
  :param pos: a 2 element tuple ``(x,y)`` specifying the position of the
              center of the picture. 
              ``(0,0)`` is top left.  ``(1,1)`` is bottom right.
  :param width: The width of the picture.  1 is the width of the window.
  :param rot: rotation of the picture in degrees.

  This class represents a picture you would create via 
  "Create>Annotations>SVG" from the menubar inside kst.
  
  Use the convenience function in Client to create an SVG picture in kst::
  
    import pykst as kst
    client = kst.Client()
    ...
    svg1 = client.new_SVG("image.svg", (0.25, 0.25), 0.2)

  """
  def __init__(self,client,filename, pos=(0.1,0.1), width=0.1, rot=0, 
               name="", new=True) :
    ViewItem.__init__(self,client)

    if (new == True):
      self.client.send("newSvgItem("+b2str(filename)+")")
      self.handle=self.client.send("endEdit()")

      self.handle.remove(0,self.handle.indexOf("ing ")+4)

      self.set_pos(pos)
      self.set_width(width)
      self.set_fixed_aspect_ratio(True)
      self.set_rotation(rot)
      self.set_name(name)
    else:
      self.handle = name      

  def set_width(self, width):
    """ set the width of the picture.
    
    The width of the window is 1.0.
    """
    self.client.send_si(self.handle,"setGeoX("+b2str(width)+")")

  @classmethod
  def getList(cls,client):
    x=client.send("getSVGList()")
    ret=[]
    while x.contains('['):
      y=x
      y.remove(0,1)
      y.remove(y.indexOf(']'),9999999)
      x.remove(0,x.indexOf(']')+1)
      ret.append(ExistingSVG(client,y))
    return ret





class Plot(ViewItem) :
  """ A plot inside kst.

  :param pos: a 2 element tuple ``(x,y)`` specifying the position. 
              ``(0,0)`` is top left.  ``(1,1)`` is bottom right.
  :param size: a 2 element tuple ``(w,h)`` specifying the size.
              ``(1,1)`` is the size of the window.
              ``(0,0)``, the default, specifies auto placement.
  :param font_size: font size for labels in the plot.  kst default if 0.
  :param rotation: rotation of the label in degrees.
  :param columns: auto-place the plot, reformatting into this many columns.
  :param fill_color: the background color.
  :param fill_style: the background fill style.  See set_fill_style.
  :param stroke_style: see set_stroke_style
  :param stroke_width: the pen width for the plot outline.
  :param stroke_brush_color: the plot outline color
  :param stroke_brush_style: see set_stroke_brush_style
  :param strokeJoinStyle: see set_stroke_join_style
  :param stroke_cap_style: see set_stroke_cap_style
  :param fix_aspect: if true, the plot will have a fixed aspect ratio.

  Colors are given by a name such as ``red`` or a hex number such 
  as ``#FF0000``. 
  
  This class represents a Plot you would create via 
  "Create>Annotations>Plot" from the menubar inside kst.
  
  To create an plot in kst and plot a curve ``curve1``::
  
    import pykst as kst
    client = kst.Client()
    ...
    P1 = client.new_plot((0.25, 0.25), (0.5,0.5))
    P1.add(curve1)

  """
  def __init__(self,client,pos=(0,0),size=(0,0),rot=0,
               font_size = 0,
               columns = 0,
               fill_color="white", fill_style=1, stroke_style=1, stroke_width=1,
               stroke_brush_color="black", stroke_brush_style=1, 
               strokeJoinStyle=1, stroke_cap_style=1, fix_aspect=False,
               name="", new=True) :
    ViewItem.__init__(self,client)

    if (new == True):
      self.client.send("newPlot()")
      if (columns>0):
        self.client.send("addToCurrentView(Columns,"+b2str(columns)+")")
      elif (size == (0,0)):
        self.client.send("addToCurrentView(Auto,2)")
      else:
        self.client.send("addToCurrentView(Protect,2)")
      self.handle=self.client.send("endEdit()")

      self.handle.remove(0,self.handle.indexOf("ing ")+4)
      if (size != (0,0)):
        self.set_pos(pos)
        self.set_size(size)

      self.set_global_font(font_size = font_size)
      self.set_fixed_aspect_ratio(fix_aspect)
      self.set_rotation(rot)

      self.set_stroke_brush_color(stroke_brush_color)
      self.set_fill_color(fill_color)
      self.set_fill_style(fill_style)
      self.set_stroke_style(stroke_style)
      self.set_stroke_width(stroke_width)
      self.set_stroke_brush_color(stroke_brush_color)
      self.set_stroke_brush_style(stroke_brush_style)
      self.set_stroke_join_style(strokeJoinStyle)
      self.set_stroke_cap_style(stroke_cap_style)
      self.set_name(name)
    else:
      self.handle = name      


  def add(self, relation) :
    """ Add a curve or an image to the plot. """
    self.client.send_si(self.handle, "addRelation(" + relation.handle + ")")

  def set_x_range(self,x0, x1) :
    """ Set X zoom range from x0 to x1 """
    self.client.send_si(self.handle, "setXRange("+b2str(x0)+","+b2str(x1)+")")

  def set_y_range(self, y0, y1) :
    """ Set Y zoom range from y0 to y1 """
    self.client.send_si(self.handle, "setYRange("+b2str(y0)+","+b2str(y1)+")")

  def set_x_auto(self) :
    """ Set X zoom range to autoscale """
    self.client.send_si(self.handle,"setXAuto()")

  def set_y_auto(self) :
    """ Set Y zoom range to autoscale """
    self.client.send_si(self.handle, "setPlotYAuto()")

  def set_x_auto_border(self) :
    """ Set X zoom range to autoscale with a small border """
    self.client.send_si(self.handle, "setPlotXAutoBorder()")

  def set_y_auto_border(self) :
    """ Set Y zoom range to autoscale with a small border """
    self.client.send_si(self.handle, "setYAutoBorder()")

  def set_x_no_spike(self) :
    """ Set X zoom range to spike insensitive autoscale """
    self.client.send_si(self.handle, "setXNoSpike()")

  def set_y_no_spike(self) :
    """ Set Y zoom range to spike insensitive autoscale """
    self.client.send_si(self.handle, "setYNoSpike()")

  def set_x_ac(self, r) :
    """ Set X zoom range to fixed range, centered around the mean.  
    
    Similar to AC coupling on an oscilloscope. 
    """
    self.client.send_si(self.handle, "setXAC("+b2str(r)+")")

  def set_y_ac(self, r) :
    """ Set Y zoom range to fixed range, centered around the mean.  
    
    Similar to AC coupling on an oscilloscope. 
    """
    self.client.send_si(self.handle, "setYAC("+b2str(r)+")")

  def set_global_font(self, family="", font_size = 0, bold=False, italic=False) :
    """ Set the global plot font.  
    
    By default, the axis labels all use this, unless they have been set 
    to use their own.
    
    If the parameter 'family' is empty, the font family will be unchanged.
    If the parameter 'font_size' is 0, the font size will be unchanged.
    The font will be bold if parameter 'bold' is set to 'bold' or 'True'.
    The font will be italic if parameter 'italic' is set to 'italic' 
    or 'True'.
    """
    self.client.send_si(self.handle, "setGlobalFont("+family+","+
                        b2str(font_size)+","+b2str(bold)+","+b2str(italic)+")")

  def set_top_label(self, label="") :
    """ Set the plot top label """
    self.client.send_si(self.handle, "setTopLabel("+label+")")

  def set_bottom_label(self, label="") :
    """ Set the plot bottom label """
    self.client.send_si(self.handle, "setBottomLabel("+label+")")

  def set_left_label(self, label="") :
    """ Set the plot left label """
    self.client.send_si(self.handle, "setLeftLabel("+label+")")

  def set_right_label(self, label="") :
    """ Set the plot right label """
    self.client.send_si(self.handle, "setRightLabel("+label+")")

  def set_top_label_auto(self) :
    """ Set the top label to auto generated. """
    self.client.send_si(self.handle, "setTopLabelAuto()")
    
  def set_bottom_label_auto(self) :
    """ Set the bottom label to auto generated. """
    self.client.send_si(self.handle, "setBottomLabelAuto()")

  def set_left_label_auto(self) :
    """ Set the left label to auto generated. """
    self.client.send_si(self.handle, "setLeftLabelAuto()")

  def set_right_label_auto(self) :
    """ Set the right label to auto generated. """
    self.client.send_si(self.handle, "setRightLabelAuto()")

  def normalize_x_to_y(self) :
    """ Adjust the X zoom range so X and Y have the same scale 
    per unit (square pixels) """
    self.client.send_si(self.handle,  "normalizeXtoY()")

  def set_log_x(self, log_mode = True) :
    """ Set X axis to log mode. """
    self.client.send_si(self.handle,  "setLogX("+b2str(log_mode) + ")")

  def set_log_y(self, log_mode = True) :
    """ Set Y axis to log mode. """
    self.client.send_si(self.handle,  "setLogY("+b2str(log_mode) + ")")

  def set_y_axis_reversed(self, reversed=True) :
    """ set the Y axis to decreasing from bottom to top. """
    if reversed == True:
      self.client.send_si(self.handle,  "setYAxisReversed()")
    else:
      self.client.send_si(self.handle,  "setYAxisNotReversed()")

  def set_x_axis_reversed(self, reversed=True) :
    """ set the X axis to decreasing from left to right. """
    if reversed == True:
      self.client.send_si(self.handle,  "setXAxisReversed()")
    else:
      self.client.send_si(self.handle,  "setXAxisNotReversed()")


class ExistingPlot(Plot):
  def __init__(self,client,handle):
    ViewItem.__init__(self,client)
    self.handle=handle
    
  @classmethod
  def getList(cls,client):
    x=client.send("getPlotList()")
    ret=[]
    while x.contains('['):
      y=x
      y.remove(0,1)
      y.remove(y.indexOf(']'),9999999)
      x.remove(0,x.indexOf(']')+1)
      ret.append(ExistingPlot(client,y))
    return ret





class Button(ViewItem) :
  """ This represents a button inside a View. When the button is pressed, it sends a message via a socket.
  
  socket is a QtNetwork.QLocalSocket that is not connected to anything. The message "clicked" will be sent
  when the button is pressed. See the bonjourMonde example. """
  def __init__(self,client,text,socket,posX=0.1,posY=0.1,sizeX=0.1,sizeY=0.1,rot=0) :
    ViewItem.__init__(self,client)
    self.client.send("newButton()")
    self.client.send("setPosX("+b2str(posX)+")")
    self.client.send("setPosY("+b2str(posY)+")")
    self.client.send("setGeoX("+b2str(sizeX)+")")
    self.client.send("setGeoY("+b2str(sizeY)+")")
    self.client.send("setText("+b2str(text)+")")
    self.client.send("setRotation("+b2str(rot)+")")
    self.handle=self.client.send("endEdit()")

    self.handle.remove(0,self.handle.indexOf("ing ")+4)
    socket.connectToServer(client.server_name)
    socket.waitForConnected(300)
    socket.write(b2str("attachTo("+self.handle+")"))
    
  def set_text(self,text):
    """ Sets the text of the button. """
    self.client.send("beginEdit("+self.handle+")")
    self.client.send("setText("+b2str(text)+")")
    self.client.send("endEdit()")





class LineEdit(ViewItem) :
  """ This represents a line edit inside a View. When the lineedit's value is changed, it sends a message via a socket.
  
  socket is a QtNetwork.QLocalSocket that is not connected to anything. The message "valueSet:VAL" where VAL is some text
  will be sent when the text is changed. See the ksNspire example. """
  def __init__(self,client,text,socket,posX=0.1,posY=0.1,sizeX=0.1,sizeY=0.1,rot=0) :
    ViewItem.__init__(self,client)
    self.client.send("newLineEdit()")
    self.client.send("setPosX("+b2str(posX)+")")
    self.client.send("setPosY("+b2str(posY)+")")
    self.client.send("setGeoX("+b2str(sizeX)+")")
    self.client.send("setGeoY("+b2str(sizeY)+")")
    self.client.send("setText("+b2str(text)+")")
    self.client.send("setRotation("+b2str(rot)+")")
    self.handle=self.client.send("endEdit()")

    self.handle.remove(0,self.handle.indexOf("ing ")+4)
    socket.connectToServer(b2str(client.server_name))
    socket.waitForConnected(300)
    socket.write(b2str("attachTo("+self.handle+")"))
    
  def set_text(self,text):
    """ Sets the text of the line edit. """
    self.client.send("beginEdit("+self.handle+")")
    self.client.send("setText("+b2str(text)+")")
    self.client.send("endEdit()")
