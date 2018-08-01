
style = {
        'figure.dpi': 180,
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
        'lines.linewidth': 1.2,
        'mathtext.fontset': 'cm',
        'mathtext.rm': 'serif'
        }


width_1col = 7.0
width_2col = 3.4


xticks = [10*i - 20.0 for i in range(5)]
yticks = [15.*i - 30.0 for i in range(5)]
zticks = [12.*i - 36.0 for i in range(5)]
xticklabels = ['']*len(xticks)
yticklabels = ['']*len(yticks)
for i in range(0,5,2):
    xticklabels[i] = '{0:.1f}'.format(10*i - 20.0)
    yticklabels[i] = '{0:.1f}'.format(15*i - 30.0)
p3attr = dict(
            aspect = .6,
            xlabel = 'X',
            ylabel = 'Y',
            zlabel = 'Z',
            xlim3d = [-20.0, 20.0],
            ylim3d = [-30.0, 30.0],
            zlim3d = [-36.0, 12.0],
            xticks = xticks,
            yticks = yticks,
            zticks = zticks,
            xticklabels = xticklabels,
            yticklabels = yticklabels
            )

bgprop = dict(
    color=(.0, .2, .8, .2),
    linewidth = 0.5,
    linestyle = '-'
    )
    
p3line_prop = dict(
        color='red', 
        marker='', 
        linestyle='-', 
        linewidth=2.0
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
    ylim = [-25.0, 25.0]
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
    