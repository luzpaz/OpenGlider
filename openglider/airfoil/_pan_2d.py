from __future__ import division
import numpy
from openglider.vector import normalize, norm
from openglider.airfoil import Profile2D

numpy.set_printoptions(precision=3)
numpy.set_printoptions(suppress=True)


class panel_methode_2d():
	def __init__(self, airfoil, aoa = 10. * numpy.pi, vel = 10., wake_numpoints = 10, wake_length = 1):
		self.aoa = aoa
		self.airfoil = airfoil
		self.q_inf = vel
		self.v_inf = numpy.multiply(vel, [[numpy.cos(self.aoa)], [numpy.sin(self.aoa)]])
		self.length = len(self.airfoil)-1
		self.mat_douplet_cooef = numpy.zeros([self.length, self.length])

		self.wake_length = wake_length
		self.wake_numpoints = wake_numpoints
		self.wake = numpy.zeros([wake_numpoints,2])
		self.inital_wake()
		self.douplet = numpy.zeros(self.length)
		self.velocity = numpy.zeros(self.length)
		self.pressure = numpy.zeros(self.length)
		self.bc_vec = numpy.zeros(self.length)
		self.panel_mids = []
		self.panel = []
		self.wake_panels = []
		self.half_lenghts = numpy.zeros(self.length)

		self.calc_panel_geo()
		self.create_mat_douplet_lin()
		self.create_bc_vec()
		self.calc_douplet()
		self.calc_velocity()
		self.calc_cp()


	def _douplet_const(self, point_j, panel):
		point_i_1, point_i_2 = panel
		t = point_i_2 - point_i_1
		n_ = normalize([t[1], -t[0]])
		pn, s0 = numpy.linalg.solve(numpy.transpose(numpy.array([n_,t])),-point_i_1 + point_j)
		l = norm(t)
		if pn == 0:
			return(0)
		else:
			return(1/2/numpy.pi*(-numpy.arctan2(pn, (s0 - 1) * l) + numpy.arctan2(pn, s0 * l)))


	def create_mat_douplet_lin(self):
		print("create douplet matrix")
		for i in range(self.length):
			for j in range(self.length):
				d_0 = self._douplet_const(self.panel_mids[i], self.panel[j])
				self.mat_douplet_cooef[i][j] = d_0
				if i==j:
					self.mat_douplet_cooef[i][j] = 1 / 2
			for j in range(len(self.wake)-1):
				wake_w = numpy.array([self.wake[j], self.wake[j+1]])
				d_0 = self._douplet_const(self.panel_mids[i], wake_w)
				self.mat_douplet_cooef[i][1] -= d_0
				self.mat_douplet_cooef[i][-2] += d_0


	def create_bc_vec(self):
		for i in range(self.length):
			self.bc_vec[i] -= self.panel_mids[i][0]*self.v_inf[0] + self.panel_mids[i][1]*self.v_inf[1]

	def calc_douplet(self):
		print("solve the system")
		lsg = numpy.linalg.solve(self.mat_douplet_cooef,self.bc_vec)
		for i in range(self.length):
			self.douplet[i] = lsg[i]

	def calc_velocity(self):
		print("calculate velocity")
		print(len(self.douplet))
		for i in range(self.length):
			d0 = self.douplet[i]
			if i == 0:
				print(i)
				dp = self.douplet[2]
				dm = self.douplet[1]
				lm = +self.half_lenghts[0] + self.half_lenghts[1]
				lp = lm + self.half_lenghts[1] + self.half_lenghts[2]
			elif i == self.length-1:
				dp = self.douplet[i-1]
				dm = self.douplet[i-2]
				lp = -self.half_lenghts[i] - self.half_lenghts[i-1]
				lm = lp-self.half_lenghts[i-1] - self.half_lenghts[i-2]
			else:
				dp = self.douplet[i+1]
				dm = self.douplet[i-1]
				lm = -self.half_lenghts[i] - self.half_lenghts[i-1]
				lp = self.half_lenghts[i] + self.half_lenghts[i+1]
			self.velocity[i] = -(((d0-dp)*lm**2 + (dm-d0)*lp**2)/(lm*(lm - lp)*lp))

	def calc_cp(self):
		print("calculate pressure")
		for i in range(self.length):
			self.pressure[i] = 1 - self.velocity[i]**2 / self.q_inf**2

	def inital_wake(self):
		for i in range(self.wake_numpoints):
			self.wake[i][0] = 1 + i *self.wake_length / self.wake_numpoints
			self.wake[i][1] = 0

	def calc_panel_geo(self):
		for i in range(self.length):
			self.panel.append(numpy.array([self.airfoil[i], self.airfoil[i+1]]))
			self.panel_mids.append((self.airfoil[i] + self.airfoil[i+1]) / 2)
			self.half_lenghts[i] = norm(self.airfoil[i]- self.airfoil[i+1])/2
		for i in range(self.wake_numpoints-1):
			self.wake_panels.append(numpy.array([self.wake[i], self.wake[i+1]]))



def test():
	p1 = numpy.array([0,0])
	p2 = numpy.array([1,0])
	pj = numpy.array([5,5])
	arf = Profile2D()
	# arf.importdat("../../tests/testprofile.dat")
	arf.compute_naca(2400)
	arf.numpoints=10
	pan = panel_methode_2d([p1,p2,pj,p1], aoa=2*numpy.pi/180.)
	print(pan._douplet_const(pj,[p1,p2]))
	print(pan._douplet_lin(pj,[p1,p2]))
	print(pan._source_const(pj,[p1,p2]))

def plot_test():
	arf = Profile2D()
	arf.importdat("/home/lo/Dropbox/modellbau/profile/pw51-9.dat")
	arf.numpoints = 200
	pan = panel_methode_2d(arf.data, aoa=10*numpy.pi/180, wake_length=5, wake_numpoints=10)
	print(pan.mat_douplet_cooef)
	from matplotlib import pyplot
	pyplot.plot(pan.pressure, marker="x")
	pyplot.show()

if __name__ == "__main__":
	plot_test()

