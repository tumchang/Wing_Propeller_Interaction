filename = "./Steady/atr72-500_out/800/atr72-500_out.su2"


def getnpoints():
    npoints = 0
    with open(filename) as f:

        for line in f:
            l = line[0:4]
            if l == "NPOI":
                npoints = line.split()[1]
                print(npoints)
                break
    f.close()
    return (npoints)


# now loop over elements and check which points are used in the mesh
def getunusedpoints():
    numberarray = list(range(0, npoints))
    print("len=", len(numberarray))
    print(numberarray[1:4])
    nelems = 0
    with open(filename) as f:
        line = f.readline()
        line = f.readline()
        if line[0:4] == "NELE":
            nelems = int(line.split()[1])
            print("number of elements=", nelems)

        counter = 0
        for line in f:
            l = line.split()
            for i in range(1, len(l) - 1):
                try:
                    numberarray[int(l[i])] = -1
                except:
                    # do nothing
                    numberarray

            if counter == nelems:
                break
            counter = counter + 1

    unusedpointsarray = []
    for i in numberarray:
        if i != -1:
            unusedpointsarray.append(i)
    return (unusedpointsarray)


npoints = int(getnpoints())
print("number of points =", npoints)
p = getunusedpoints()
print(p)
