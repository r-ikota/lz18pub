style = {
        'figure.dpi': 160,
        'figure.figsize': [4.8, 3.6],
        'font.family': 'serif',
        'font.size': 10,
        'axes.labelsize': 12,
        'axes.labelweight': 'bold',
        'axes.titlesize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 12,
        'lines.linewidth': 1.2
    }


width_1col = 5.4
width_2col = 2.8

p3attr = dict(
            aspect = .8,
            xlabel = 'X',
            ylabel = 'Y',
            zlabel = 'Z',
            xlim3d = [-20.0, 20.0],
            ylim3d = [-25.0, 25.0],
            zlim3d = [-35.0, 15.0],
            xticks = [10*i for i in range(-2,3)],
            yticks = [10*i for i in range(-2,3)],
            zticks = [10*i for i in range(-3,2)]
            )

bgprop = dict(
    color=(.0, .2, .8, .2),
    linewidth = 0.5,
    linestyle = '-'
    )
    
p3line_prop = dict(
        color=(0,0,0,0.7), 
        marker='x',
        markersize = 4.0
    )

animAttr = dict(
                blit=True,
                interval=20,
                repeat=False
            )

pEigattr = dict(
    xlabel = 'Re',
    ylabel = 'Im',
    xlim = [-25.0, 15.0],
    ylim = [-25.0, 25.0],
    xticks = [5.0*i for i in range(-5,4)],
    yticks = [10.0*i for i in range(-2,3)],
    aspect = 0.8
    )
    
eig2DLineProp = [
                dict(
                    color = 'red', 
                    marker='o',
                    markersize=4.0
                    )
                ]*3 + \
                [dict(
                    color='blue', 
                    marker='x',
                    markersize=5.0
                    )
                  ]*3
    