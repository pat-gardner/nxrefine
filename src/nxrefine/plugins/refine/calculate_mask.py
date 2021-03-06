from nexpy.gui.pyqt import QtCore, QtWidgets
import numpy as np
from nexpy.gui.datadialogs import BaseDialog, GridParameters
from nexpy.gui.utils import report_error
from nexusformat.nexus import *

from nxrefine.nxlock import Lock, LockException
from nxrefine.nxreduce import NXReduce


def show_dialog():
    try:
        dialog = Mask3DDialog()
        dialog.show()
    except NeXusError as error:
        report_error("Calculating 3D Mask", error)


class Mask3DDialog(BaseDialog):

    def __init__(self, parent=None):
        super(Mask3DDialog, self).__init__(parent)

        self.select_entry(self.choose_entry)

        self.parameters = GridParameters()
        self.parameters.add('radius', 200, 'Radius')
        self.parameters.add('width', 3, 'Frame Width')
        self.set_layout(self.entry_layout, 
                        self.parameters.grid(),
                        self.action_buttons(('Calculate 3D Mask', self.calculate_mask)),
                        self.progress_layout(save=True))
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.set_title('Calculate 3D Mask')
        self.reduce = None

    def choose_entry(self):
        self.reduce = NXReduce(self.entry)

    @property
    def radius(self):
        return self.parameters['radius'].value

    @property
    def width(self):
        return self.parameters['width'].value

    def calculate_mask(self):
        self.check_lock(self.reduce.wrapper_file)
        self.thread = QtCore.QThread()
        self.reduce = NXReduce(self.entry, radius=self.radius, width=self.width,
                               mask=True, overwrite=True, gui=True)
        self.reduce.moveToThread(self.thread)
        self.reduce.start.connect(self.start_progress)
        self.reduce.update.connect(self.update_progress)
        self.reduce.result.connect(self.calculate_mask)
        self.reduce.stop.connect(self.stop)
        self.thread.started.connect(self.reduce.nxfind)
        self.thread.start(QtCore.QThread.LowestPriority)

    def check_lock(self, file_name):
        try:
            with Lock(file_name, timeout=2):
                pass
        except LockException as error:
            if self.confirm_action('Clear lock?', str(error)):
                Lock(file_name).release()

    def calculate_mask(self, mask):
        self.mask = mask

    def stop(self):
        self.stop_progress()
        if self.thread and self.thread.isRunning():
            self.reduce.stopped = True
            self.thread.exit()

    def accept(self):
        try:
            with Lock(self.reduce.wrapper_file):
                self.reduce.write_peaks(self.peaks)
        except LockException as error:
            if self.confirm_action('Clear lock?', str(error)):
                Lock(self.reduce.wrapper_file).release()
        if self.thread:
            self.stop()
        super(Mask3DDialog, self).accept()

    def reject(self):
        if self.thread:
            self.stop()
        super(Mask3DDialog, self).reject()
