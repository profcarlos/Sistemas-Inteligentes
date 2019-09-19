#!/usr/bin/env python
# -----------------------------------------------------------------------------
# Self-organizing map
# Copyright (C) 2011  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License.
# -----------------------------------------------------------------------------
import numpy as np
import time

def fromdistance(fn, shape, center=None, dtype=float):
    def distance(*args):
        d = 0
        for i in range(len(shape)):
            d += ((args[i]-center[i])/float(max(1,shape[i]-1)))**2
        return np.sqrt(d)/np.sqrt(len(shape))
    if center == None:
        center = np.array(list(shape))//2
    return fn(np.fromfunction(distance,shape,dtype=dtype))

def Gaussian(shape,center,sigma=0.5):
    ''' '''
    def g(x):
        return np.exp(-x**2/sigma**2)
    return fromdistance(g,shape,center)

class SOM:
    ''' Self-organizing map '''

    def __init__(self, *args):
        ''' Initialize som '''
        self.codebook = np.zeros(args)
        self.reset()

    def reset(self):
        ''' Reset weights '''
        self.codebook = np.random.random(self.codebook.shape)

    def learn(self, samples, epochs=10000, sigma=(10, 0.001), lrate=(0.5,0.005)):
        ''' Learn samples '''
        sigma_i, sigma_f = sigma
        lrate_i, lrate_f = lrate

        for i in range(epochs):
            print("----------- i: {}".format(i))
            # Adjust learning rate and neighborhood
            t = i/float(epochs)
            lrate = lrate_i*(lrate_f/float(lrate_i))**t
            sigma = sigma_i*(sigma_f/float(sigma_i))**t
            print("lrate: {} sigma: {}".format(lrate, sigma))

            # Get random sample
            index = np.random.randint(0,samples.shape[0])
            data = samples[index]
            print("index: {} data: {}".format(index, data))

            # Get index of nearest node (minimum distance)
            D = ((self.codebook-data)**2).sum(axis=-1)
            winner = np.unravel_index(np.argmin(D), D.shape)
            print("D: {} winner: {}".format(D, winner))

            # Generate a Gaussian centered on winner
            G = Gaussian(D.shape, winner, sigma)
            G = np.nan_to_num(G)
            print("G: {}".format(G))

            # Move nodes towards sample according to Gaussian 
            delta = self.codebook-data
            print("codebook [t  ]: {}".format(self.codebook))
            for i in range(self.codebook.shape[-1]):
                self.codebook[...,i] -= lrate * G * delta[...,i]
            print("codebook [t+1]: {}".format(self.codebook))

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import matplotlib
    import matplotlib.pyplot as plt
    try:    from voronoi import voronoi
    except: voronoi = None

    def learn(network, samples, epochs=10, sigma=(10, 0.01), lrate=(0.5,0.005)):
        network.learn(samples, epochs)
        fig = plt.figure(figsize=(10,10))
        axes = fig.add_subplot(1,1,1)
        # Draw samples
        x,y = samples[:,0], samples[:,1]
        plt.scatter(x, y, s=1.0, color='b', alpha=0.1, zorder=1)
        # Draw network
        x,y = network.codebook[...,0], network.codebook[...,1]
        if len(network.codebook.shape) > 2:
            for i in range(network.codebook.shape[0]):
                plt.plot (x[i,:], y[i,:], 'k', alpha=0.85, lw=1.5, zorder=2)
            for i in range(network.codebook.shape[1]):
                plt.plot (x[:,i], y[:,i], 'k', alpha=0.85, lw=1.5, zorder=2)
        else:
            plt.plot (x, y, 'k', alpha=0.85, lw=1.5, zorder=2)
        plt.scatter (x, y, s=50, c='w', edgecolors='k', zorder=3)
        if voronoi is not None:
            segments = voronoi(x.ravel(),y.ravel())
            lines = matplotlib.collections.LineCollection(segments, color='0.65')
            axes.add_collection(lines)
        plt.axis([0,1,0,1])
        plt.xticks([]), plt.yticks([])
        plt.show()
        time.sleep(5)

    # Example 1: 2d uniform distribution (1d)
    # -------------------------------------------------------------------------
    print('One-dimensional SOM over two-dimensional uniform square')
    som = SOM(4,2)
    samples = np.random.random((100,2))
    learn(som, samples)
