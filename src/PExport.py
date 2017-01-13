

class Export(object):
    """docstring for Export"""
    def __init__(self, arg):
        super(Export, self).__init__()
        self.arg = arg

    def exportFLMA(self, blocks, name='', depth=0.1):

        lines = list()

        numvertex = '8'

        # loop over all individual mesh blocks
        for block in blocks:

            U, V = block.getDivUV()
            points = (U + 1) * (V + 1)

            # write number of points to FLMA file (*2 for z-direction)
            lines.append(str(2 * points) + '\n')

            signum = -1.

            # write x-, y- and z-coordinates to FLMA file
            # loop 1D direction (symmetry)
            for j in range(2):
                for uline in block.getULines():
                    for i in range(len(uline)):
                        lines.append(str(uline[i][0]) + ' ' +
                                     str(uline[i][1]) +
                                     ' ' + str(signum * depth / 2.0) + ' ')
                signum = 1.

            # write number of cells to FLMA file
            cells = U * V
            lines.append('\n' + str(cells) + '\n')

            # write cell connectivity to FLMA file
            up = U + 1
            vp = V + 1
            for i in range(U):
                for j in range(V):

                    p1 = j * up + i + 1
                    p2 = (vp + j) * up + i + 1
                    p3 = p2 - 1
                    p4 = p1 - 1
                    p5 = (j + 1) * up + i + 1
                    p6 = (vp + j + 1) * up + i + 1
                    p7 = p6 - 1
                    p8 = p5 - 1

                    connectivity = str(p1) + ' ' + str(p2) + ' ' + str(p3) + \
                        ' ' + str(p4) + ' ' + str(p5) + ' ' + str(p6) + \
                        ' ' + str(p7) + ' ' + str(p8) + '\n'

                    lines.append(numvertex + '\n')
                    lines.append(connectivity)

            # write FIRE element type (FET) to FLMA file
            fetHEX = '5'
            lines.append('\n' + str(cells) + '\n')
            for i in range(cells):
                lines.append(fetHEX + ' ')
            lines.append('\n\n')

            # write FIRE selections to FLMA file
            lines.append('0')

        filename = name
        with open(filename, 'w') as f:
            for line in lines:
                f.write(line)
