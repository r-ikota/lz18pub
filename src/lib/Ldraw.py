import numpy as np
import h5py
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from scipy.integrate import cumtrapz
import time, os, subprocess, tempfile, shutil
from abc import ABCMeta, abstractmethod
from subprocess import call

FFMpegWriter = animation.writers['ffmpeg']

class Frame(metaclass=ABCMeta):
    def __init__(self,
        data,
        **attr
        ):
        self.data = data.copy()
        self.fig = plt.figure(**attr)
        self.panes = []
        self.tarray = data['tarray']

    def _addPane(self, pane):
        self.panes.append(pane)
        
    def trange2Index(self, trange = None):
        '''
        Return a slice object that correnponds to trange.

        trange: (t0, t1)
            t0 < t1
        returned value: slice(i0, i1)
            self.tarray(i0) ~= t0
            self.tarray(i1) ~= t1
        '''

        tarray = self.tarray
        eps = 1.0e-5
        
        if trange == None: return slice(0, len(tarray))
        alpha = np.where(tarray > trange[0] - eps)[0]
        omega = np.where(tarray < trange[1] + eps)[0]
        if (len(alpha)*len(omega) != 0) and (alpha[0] < omega[-1]):
            return slice(alpha[0], omega[-1]+1)
        else:
            return slice(len(tarray) - 1, len(tarray))

    def time2Index(self, time = None):
        '''
        Return an index that corresponds to time.

        time: fload

        returned value: i0 (int)
            self.tarray(i0) ~= time
        '''

        tarray = self.tarray
        eps = 1.0e-5
        if time == None: 
            return slice(0,1)

        elif time > tarray[-1] - eps: 
            return slice(-1, None)
            
        alpha = np.where(tarray > time - eps)[0][0]
        return slice(alpha, alpha + 1)
        
    def _plot(self, index):
        _ret = []
        for pane in self.panes:
            _ret += pane._plot(index, self.data)
        return _ret

    def reset(self):
        _ret = []
        for pane in self.panes:
            _ret += pane._reset()
        return _ret

    def plotSnap(self, time):
        '''
        plot Snap for t = time.
        time: float
        '''

        self._plot(self.time2Index(time))

    def plotTrail(self, trange):
        '''
        plot Trail for trange.
        trange: (t0, t1); t0 < t1: floats
        '''

        self._plot(self.trange2Index(trange))

    def _updatePanes(self, i):
        return self._plot(i)

    def animate(self, trange=None, **attr):
        '''
        trange: (t0,t1); t0 < t1: floats
        '''

        index = self.trange2Index(trange)
        #input('Hit Enter to Start.');
        self._ani = animation.FuncAnimation(
            self.fig,
            self._updatePanes,
            range(index.start,index.stop),
            **attr
        )

    def mkMov(
            self, 
            fpath,
            trange=None, 
            fps=15, 
            dpi=120, 
            **prop
            ):
        '''
        fpath: file path
        trange: (t0, t1); t0 < t1
        fps: frame per second
        dpi: dots per inch
        '''
        
        index = self.trange2Index(trange)
        moviewriter = FFMpegWriter(fps)
        with moviewriter.saving(
                    self.fig, fpath, dpi=dpi
                        ):
            for i in range(index.start, index.stop):
                self._updatePanes(i)
                moviewriter.grab_frame()
            
        
class LFrame(Frame):
    def __init__(self, data, **attr):
        Frame.__init__(self, data, **attr)
        if ('eigValDF' in data) and ('eigValSymDF' in data):
            evDF = data['eigValDF']
            evDFre = np.real(evDF)
            evDFim = np.imag(evDF)
            evS = data['eigValSymDF']
            evSre = np.real(evS)
            evSim = np.imag(evS)

            evRe = np.hstack((evDFre, evSre))
            evIm = np.hstack((evDFim, evSim))
            
            self.data['eigValRe'] = np.transpose(evRe)
            self.data['eigValIm'] = np.transpose(evIm)



class Pane(metaclass=ABCMeta):
    def __init__(self, frame, gs, **attr):
        self.frame = frame
        self.attr = attr
        self.lines = None
        self.ax = None
        self._set(frame.fig, gs, **attr)
        frame._addPane(self)

    @abstractmethod
    def _set(self, fig, gs, **attr):
        pass

    @abstractmethod
    def _reset(self):
        pass

    @abstractmethod
    def _plot(self, index, data):
        pass

    def plotSnap(self, time):
        '''
        plot Snap for t = time.
        time: float
        '''
        
        self._plot(
            self.frame.time2Index(time),
            self.frame.data
            )

    def plotTrail(self, trange):
        '''
        plot Trail for trange.
        trange: (t0, t1); t0 < t1: floats
        '''

        self._plot(
            self.frame.trange2Index(trange),
            self.frame.data
            )        

    def set_line_prop(self, attr_list):
        '''
        set line properties.

        attr_list: 
            list of line properties.
            each property is a dictionary.
        '''

        if  self.lines == None:
            print('This pane does not have lines.')
            return False
        
        for l, attr in zip(self.lines, attr_list):
            l.set(**attr)
            
    def set_label(
            self, 
            label, 
            xy=(-0.08, 0.9), 
            **attr
            ):
            self._label = self.ax.annotate(
                    label,
                    xy,
                    xycoords="axes fraction", 
                    va="top", ha="right"
                    )


class Pane3D(Pane):
    def _set(self, fig, gs, **attr):
        self.ax = fig.add_subplot(
                        gs, 
                        projection='3d',
                        **attr
                        )
    
class Pane2D(Pane):
    def _set(self, fig, gs, **attr):
        self.ax = fig.add_subplot(
                    gs,
                    **attr
                    )

class PaneTime(Pane2D):
    def __init__(
                self, 
                frame, 
                gs, 
                tformat='time = {0:07.2f}', 
                **attr
                ):
        Pane.__init__(self, frame, gs, **attr)
        self.tformat = tformat

    def _set(self, fig, gs, **attr):
        Pane2D._set(self, fig, gs, **attr)
        ax = self.ax
        ax.set_xlim([-1., 1.])
        ax.set_ylim([-1., 1.])
        ax.set_axis_off()
        self.txt = ax.text(
                0.0, 0.0, 
                '',
                horizontalalignment='center',
                verticalalignment='bottom'
                )

    def _plot(self, index, data):
        tarray = data['tarray']
        if type(index) == slice:
            i = index.start
        else:
            i = index
        time = tarray[i]
        self.txt.set_text(self.tformat.format(time))
        return self.txt,

    def _reset(self):
        self.txt.set_text('')
        return self.txt,

class PanePhase3D(Pane3D):
    def __init__(self, frame, gs, **attr):
        Pane3D.__init__(self, frame, gs, **attr)
        self.bglines = None

    def _set(self, fig, gs, **attr):
        Pane3D._set(self, fig, gs, **attr)
        self.lines = self.ax.plot([],[],[])

    def _plot(self, index, data):
        _xyz = data['xyz'][index]
        x = _xyz[:,0]
        y = _xyz[:,1]
        z = _xyz[:,2]
        l = self.lines[0]
        l.set_data([x,y])
        l.set_3d_properties(z)

        return self.lines

    def _reset(self):
        l = self.lines[0]
        l.set_data([[],[]])
        l.set_3d_properties([])

        return self.lines

    def setBG(self, fpath = None, **attr):
        if fpath == None:
            dpath = os.path.split(__file__)[0]
            fpath = os.path.join(
                        dpath, 'data', 'attractor0.hdf5'
                        )
            with h5py.File(fpath, 'r') as fh:
                bgdata = fh['xyz'][()]
                x,y,z =  bgdata.T
                self.bglines = self.ax.plot(x,y,z)
            self.setBGProp(**attr)

    def setBGProp(self, **attr):
        if not self.bglines:
            print('not set BackGround.')
            return False
        else:
            l, = self.bglines
            l.set(**attr)



class PanePhase3DM(PanePhase3D):
    def _set(self, fig, gs, **attr):
        Pane3D._set(self, fig, gs, **attr)
        nfold = len(self.frame.data['xyz'])
        self.lines = []
        for i in range(nfold):
            self.lines += self.ax.plot([],[],[])

    def _plot(self, index, data):
        for l, xyz in zip(self.lines, data['xyz']):
            _xyz = xyz[index]
            x,y,z = np.transpose(_xyz)
            l.set_data([x,y])
            l.set_3d_properties(z)
            
        return self.lines

    def _reset(self):
        for l in self.lines:
            l.set_data([[],[]])
            l.set_3d_properties([])
        return self.lines

class PaneEig2D(Pane2D):
    def _set(self, fig, gs, **attr):
        Pane2D._set(self, fig, gs, **attr)
        self.lines = []
        for i in range(6):
            self.lines += self.ax.plot([],[])

    def _plot(self, index, data):
        evRe = data['eigValRe']
        evIm = data['eigValIm']

        for l, eigRe, eigIm in zip(
                        self.lines,
                        evRe,
                        evIm
                        ):
            
            l.set_data(eigRe[index], eigIm[index])
        return self.lines


    def _reset(self):
        for l in self.lines:
            l.set_data([[],[]])
        return self.lines
