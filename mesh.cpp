#include "inmost.h"

#include <cmath>
#include <cstdlib>
#include <iostream>

using namespace INMOST;
using namespace std;

int main(int argc, char *argv[])
{
	if (argc < 2) {
		cout << "Usage: mesh <input.vtk> [output.vtu] [cx cy cz]" << endl;
		cout << "  default output: mosreg_with_vectors.vtu" << endl;
		cout << "  default center: Serpukhov (assignment 3)" << endl;
		return -1;
	}

	const char *out_file = (argc >= 3) ? argv[2] : "mosreg_with_vectors.vtu";

	double cx = 141.8237539030878;
	double cy = 81.97640800277543;
	double cz = 0.0;
	if (argc >= 6) {
		cx = atof(argv[3]);
		cy = atof(argv[4]);
		cz = atof(argv[5]);
	}

	Mesh mesh;
	mesh.Load(argv[1]);

	if (mesh.GetDimensions() == 2) {
		mesh.SetDimensions(3);
		for (Mesh::iteratorNode inode = mesh.BeginNode(); inode != mesh.EndNode(); inode++) {
			Storage::real_array c = inode->RealArray(mesh.CoordsTag());
			const double z = (c.size() > 2) ? static_cast<double>(c[2]) : 0.0;
			c[0] = static_cast<Storage::real>(c[0]);
			c[1] = static_cast<Storage::real>(c[1]);
			c[2] = static_cast<Storage::real>(z);
		}
	}

	Tag tagRadius = mesh.CreateTag("RadiusNormal", DATA_REAL, NODE, NONE, 3);

	for (Mesh::iteratorNode inode = mesh.BeginNode(); inode != mesh.EndNode(); inode++) {
		double xn[3] = {0.0, 0.0, 0.0};
		inode->Barycenter(xn);

		inode->RealArray(tagRadius)[0] = static_cast<Storage::real>(xn[0] - cx);
		inode->RealArray(tagRadius)[1] = static_cast<Storage::real>(xn[1] - cy);
		inode->RealArray(tagRadius)[2] = 0.0;
	}

	mesh.Save(out_file);
	cout << "Saved " << out_file << " (tag RadiusNormal, NODE, size 3)" << endl;

	return 0;
}
