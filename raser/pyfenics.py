# -*- encoding: utf-8 -*-
'''
@Description: Calculate the weighting potential and electric field wiht fenics      
@Date       : 2021/08/31 15:04:25
@Author     : tanyuhang
@version    : 1.0
'''

import fenics
import mshr

#Calculate the weighting potential and electric field
class FenicsCal:
    def __init__(self,my_d,fen_dic):
        self.det_model = fen_dic['det_model']
        self.fl_x=my_d.l_x/fen_dic['xyscale']  
        self.fl_y=my_d.l_y/fen_dic['xyscale']
        if self.det_model != "plugin3D":
            self.fl_z=my_d.depletion_depth
        else:
            self.fl_z=my_d.l_z

        self.tol = 1e-14
        self.bias_voltage = my_d.voltage
        if self.det_model == "planarRing":
            # under construction
            self.e_r_inner = my_d.e_r_inner
            self.e_r_outer = my_d.e_r_outer

        self.generate_mesh(my_d,fen_dic['mesh'])
        self.V = fenics.FunctionSpace(self.mesh3D, 'P', 1)
        self.u_bc,self.u_w_bc = self.boundary_definition(my_d)
        self.weighting_potential(my_d)
        self.electric_field(my_d)

    def generate_mesh(self,my_d,mesh_number):
        """
        @description: 
            Define the fenics solver space 
        @param:
            None
        @Returns:
            Fenics Box structure
        @Modify:
            2021/08/31
        """
        if "plugin3D" in self.det_model:
            self.sensor_range_confirm(my_d)
            m_sensor = mshr.Box(fenics.Point(self.sx_l,self.sy_l, 0), 
                                fenics.Point(self.sx_r,self.sy_r, self.fl_z))
            for i in range(len(my_d.e_tr)):
                e_t_i = my_d.e_tr[i]
                elec_n = mshr.Cylinder(fenics.Point(e_t_i[0],e_t_i[1],e_t_i[3]), 
                                       fenics.Point(e_t_i[0],e_t_i[1],e_t_i[4]),
                                       e_t_i[2],e_t_i[2])
                m_sensor = m_sensor - elec_n 
            self.mesh3D = mshr.generate_mesh(m_sensor,mesh_number)

        elif "planar3D" in self.det_model or "planarRing" in self.det_model:
            m_sensor = mshr.Box(fenics.Point(0, 0, 0), 
                                fenics.Point(self.fl_x, self.fl_y, self.fl_z))
            self.mesh3D = mshr.generate_mesh(m_sensor,mesh_number)

        elif "lgad3D" in self.det_model: # under construction
            self.mesh3D = fenics.BoxMesh(fenics.Point(0, 0, 0),
                                         fenics.Point(self.fl_x, self.fl_y, self.fl_z), 
                                         5, 5, int(mesh_number))
        
        else:
            raise(NameError)        
    
    def sensor_range_confirm(self,my_d):
        """
        @description:
            confirm the sensor range 
            at x,y axes to avoid the the big sensor size
            which will lead to complicated mesh
        @param:
            xv_min - fenics sensor x left value
            xv_max - fenics sensor x right value
            yv_min - fenics sensor y left value
            yv_max - fenics sensor y right value          
        @Modify:
            2021/08/31
        """    
        xv_list=[]
        yv_list=[]
        rest_length=50 #um
        length_flag = 0
        for i in range(len(my_d.e_tr)):
            e_t_i = my_d.e_tr[i]
            xv_list.append(e_t_i[0])
            yv_list.append(e_t_i[1])
            ele_radius= e_t_i[2]
        while length_flag == 0:
            xv_max = max(xv_list)+ele_radius+rest_length
            xv_min = min(xv_list)-ele_radius-rest_length
            yv_max = max(yv_list)+ele_radius+rest_length
            yv_min = min(yv_list)-ele_radius-rest_length
            if xv_max >= yv_max:
                yv_max = xv_max
            else:
                xv_max = yv_max
            if xv_min <= yv_min:
                yv_min = xv_min
            else:
                xv_min = yv_min
            if (xv_max > my_d.l_x or xv_min < 0
               or yv_max > my_d.l_y or yv_min < 0):
                rest_length -= 1
            else:
                length_flag = 1
        self.sx_l=xv_min
        self.sx_r=xv_max
        self.sy_l=yv_min
        self.sy_r=yv_max

    def boundary_definition(self,my_d):
        if "plugin3D" in self.det_model:
            u_bc_l = []
            u_bc_l = self.boundary_definition_3D(my_d,my_d.voltage,0.0)
            u_w_bc_l = []
            u_w_bc_l = self.boundary_definition_3D(my_d,0.0,1.0)     
        elif "planar3D" in self.det_model or "lgad3D" in self.det_model:
            u_bc_l = self.boundary_definition_planar(my_d,my_d.voltage,0.0)
            u_w_bc_l = self.boundary_definition_planar(my_d,0.0,1.0)
        elif "planarRing" in self.det_model:
            u_bc_l = self.boundary_definition_planar(my_d,my_d.voltage,0.0)
            u_w_bc_l = self.boundary_definition_ring(my_d,0.0,1.0)
        elif "planarStrip" in self.det_model:
            #under construction
            #u_bc_l = self.boundary_definition_planar(my_d,my_d.voltage,0.0)
            #u_w_bc_l = self.boundary_definition_strip(my_d,0.0,1.0)
            pass
        else:
            raise NameError(self.det_model)

        return u_bc_l, u_w_bc_l

    def boundary_definition_3D(self,my_d,p_ele,n_ele):
        """
        @description:
            Get boundary definition of 3D detector with Possion and Laplace equations
        @Modify:
            2021/08/31
        """
        bc_l = []
        for i in range (len(my_d.e_tr)):
            e_i = my_d.e_tr[i]
            str_e = "x[0]>={e_0}-{e_2} && x[0]<={e_0}+"\
                    +"{e_2} && x[1]>={e_1}-{e_2} && "\
                    +"x[1]<={e_1}+{e_2} && x[2]>={e_3} \
                    && x[2]<={e_4} && on_boundary"
            elec_p = str_e.format(e_0=e_i[0], e_1=e_i[1],
                                  e_2=e_i[2], e_3=e_i[3],
                                  e_4=e_i[4])
            if e_i[5] == "p":
                bc = fenics.DirichletBC(self.V, p_ele, elec_p)
            else:
                bc = fenics.DirichletBC(self.V, n_ele, elec_p)
            bc_l.append(bc)

        x_center = my_d.e_tr[0][0]
        y_center = my_d.e_tr[0][1]
        str_e = "(x[0]-{e_0})*(x[0]-{e_0}) +(x[1]-{e_1})*(x[1]-{e_1}) >= {e_2}*{e_2}"  
        elec_p = str_e.format(e_0=x_center, e_1=y_center,
                              e_2=my_d.e_gap)        
        out_colomn = fenics.DirichletBC(self.V, n_ele, elec_p)
        bc_l.append(out_colomn)
        return bc_l

    def boundary_definition_planar(self,my_d,p_ele,n_ele):
        """
        @description:
            Get boundary definition of planar detector with Possion and Laplace equations
        @Modify:
            2021/08/31
        """
        u_D = fenics.Expression('x[2]<tol ? p_1:p_2',
                                degree = 2, tol = 1E-14,
                                p_1 = p_ele, p_2 = n_ele)

        def boundary(x, on_boundary):
            return abs(x[2])<self.tol or abs(x[2]-self.fl_z)<self.tol
        bc_l = fenics.DirichletBC(self.V, u_D, boundary)
        return bc_l
    
    def boundary_definition_ring(self,my_d,p_ele,n_ele):
        u_D = fenics.Expression('x[2]<tol ? p_1:p_2',
                                degree = 2, tol = 1E-14,
                                p_1 = p_ele, p_2 = n_ele)
        def boundary(x, on_boundary):
            #under construction
            return (abs(x[2])<self.tol
                    and (((x[0]-my_d.l_x/2)**2 + (x[1]-my_d.l_y/2)**2) > self.e_r_inner**2
                    and ((x[0]-my_d.l_x/2)**2 + (x[1]-my_d.l_y/2)**2) < self.e_r_outer**2)
                    or abs(x[2]-self.fl_z)<self.tol)
        bc_l = fenics.DirichletBC(self.V, u_D, boundary)
        return bc_l 

    def weighting_potential(self,my_d):  
        """
        @description:
            Solve Laplace equation to 
            get weighting potential and weighting electric field
        @Modify:
            2021/08/31
        """
        # Define variational problem
        # original problem: -Δu_w = 0
        u_w = fenics.TrialFunction(self.V)
        v_w = fenics.TestFunction(self.V)
        f_w = fenics.Constant(0)
        a_w = fenics.dot(fenics.grad(u_w), fenics.grad(v_w))*fenics.dx
        L_w = f_w*v_w*fenics.dx
        # Compute solution
        self.u_w = fenics.Function(self.V)
        fenics.solve(a_w == L_w, self.u_w, self.u_w_bc)

    def electric_field(self,my_d):    
        """
        @description:
            Solve Poisson equation to get potential and electric field
        @Modify:
            2021/08/31
        """
        # Define variational problem
        # original problem: -Δu = f
        u = fenics.TrialFunction(self.V)
        v = fenics.TestFunction(self.V)
        f = self.f_expression(my_d)
        a = fenics.dot(fenics.grad(u), fenics.grad(v))*fenics.dx
        L = f*v*fenics.dx
        # Compute solution
        self.u = fenics.Function(self.V)
        fenics.solve(a == L, self.u, self.u_bc,
                     solver_parameters=dict(linear_solver='gmres',
                     preconditioner='ilu'))
        # Calculate electric field
        W = fenics.VectorFunctionSpace(self.mesh3D, 'P', 1)
        self.grad_u = fenics.project(fenics.as_vector((self.u.dx(0),
                                                       self.u.dx(1),
                                                       self.u.dx(2))),W)

    def electric_field_with_carrier(self,my_d):    
        """
        @description:
            Solve Poisson equation with carrier density 
            to get potential and electric field of undepleted device
        @Modify:
            2023/03/13
        """
        # Define variational problem
        # original problem: -Δu = f(1-exp(±u/u_T)), + for n-doped bulk and - for p
        # u_var = exp(±u/u_T)

        # under construction
        
        kboltz=8.617385e-5 #eV/K
        u_T = kboltz * my_d.temperature/1 # u_T = kT/q

        def q(u):
            "Return nonlinear coefficient"
            if my_d.voltage <0:
                return 1 - fenics.exp(u/u_T)**2
            else:
                return 1 - fenics.exp(-u/u_T)**2

        u = fenics.TrialFunction(self.V)
        v = fenics.TestFunction(self.V)
        f = self.f_expression(my_d)
        F = fenics.dot(fenics.grad(u), fenics.grad(v))*fenics.dx - f*v*(q(u))*fenics.dx
        # Compute solution
        self.u = fenics.Function(self.V)
        fenics.solve(F == 0, self.u, self.u_bc,
                     solver_parameters=dict(linear_solver='gmres',
                     preconditioner='ilu'))
        # Calculate electric field
        W = fenics.VectorFunctionSpace(self.mesh3D, 'P', 1)
        self.grad_u = fenics.project(fenics.as_vector((self.u.dx(0),
                                                       self.u.dx(1),
                                                       self.u.dx(2))),W)
        
    def f_expression(self,my_d):
        """
        @description: 
            Cal f_value of Poisson equation
        @param:
            perm_mat -- Dielectric constant of using material
                     -- 11.7 Silicon
                     -- 9.76 Silicon carbide
        @Modify:
            2021/08/31
        """
        if my_d.material == 'Si':
            perm_mat = 11.7  
        elif my_d.material == 'SiC':
            perm_mat = 9.76  
        else:
            raise NameError(my_d.material)
             
        e0 = 1.60217733e-19
        perm0 = 8.854187817e-12   #F/m
        if "lgad3D" in self.det_model:
            if my_d.part == 2:
                f = fenics.Expression('x[2] < width + tol ? charge1 : charge2',\
                                      degree = 0, width = my_d.avalanche_bond,\
                                      charge1 = e0*my_d.doping1*1e6/perm0/perm_mat,\
                                      charge2 = e0*my_d.doping2*1e6/perm0/perm_mat,\
                                      tol = self.tol)
            elif my_d.part == 3:
                f = fenics.Expression('x[2] < width1 - tol ? charge1 : (x[2] > width2 + tol ? charge3 : charge2)',\
                                      degree = 0, width1 = my_d.control_bond, width2 = my_d.avalanche_bond,\
                                      charge1 = e0*my_d.doping1*1e6/perm0/perm_mat,\
                                      charge2 = e0*my_d.doping2*1e6/perm0/perm_mat,\
                                      charge3 = e0*my_d.doping3*1e6/perm0/perm_mat,\
                                      tol = self.tol)
            else:
                raise ValueError
        else:
            f = fenics.Constant(e0*my_d.d_neff*1e6/perm0/perm_mat)
        return f

    def get_w_p(self,px,py,pz):
        """
        @description: 
            Get weighting potential at the (x,y,z) position
        @param:
            threeD_out_column -- threeD_out_column = False
                      -- Position (x,y,z) don't exit in sensor fenics range
        @reture:
            Get weighting potential at (x,y,z) position
        @Modify:
            2021/08/31
        """
        threeD_out_column=self.threeD_out_column(px,py,pz)
        if threeD_out_column:   
            f_w_p = 1.0
        else:
            scale_px=px%self.fl_x
            scale_py=py%self.fl_y
            scale_pz=pz
            try:
                f_w_p = self.u_w(scale_px,scale_py,scale_pz)
            except RuntimeError:
                f_w_p = 0.0
        return f_w_p

    def get_potential(self,px,py,pz):
        """
        @description: 
            Get potential at the (x,y,z) position
        @param:
            threeD_out_column -- threeD_out_column = False
                      -- Position (x,y,z) don't exit in sensor fenics range
        @reture:
            Get potential at (x,y,z) position
        @Modify:
            2021/08/31
        """
        threeD_out_column=self.threeD_out_column(px,py,pz)
        if threeD_out_column:
            f_p = 0
        else:
            scale_px=px%self.fl_x
            scale_py=py%self.fl_y
            scale_pz=pz   
            try:
                f_p = self.u(scale_px,scale_py,scale_pz)
            except RuntimeError:
                f_p = 0.0
        return f_p
            
    def get_e_field(self,px,py,pz):
        """
        @description: 
            Get eletric field at the px,py,pz position in V/um
        @param:
            threeD_out_column -- threeD_out_column = False
                      -- Position (x,y,z) don't exit in sensor fenics range
        @reture:
            Eletric field along x,y,z direction
        @Modify:
            2021/08/31
        """
        threeD_out_column=self.threeD_out_column(px,py,pz)
        if threeD_out_column:   
            x_value,y_value,z_value = 0,0,0
        else:
            scale_px=px%self.fl_x
            scale_py=py%self.fl_y
            scale_pz=pz
            try:
                x_value,y_value,z_value = self.grad_u(scale_px,scale_py,scale_pz)
                x_value = x_value* -1
                y_value = y_value* -1
                z_value = z_value* -1
            except RuntimeError:
                x_value,y_value,z_value = 0,0,0
        
        return x_value,y_value,z_value

    def threeD_out_column(self,px,py,pz):
        """
        @description: 
           Judge whether (x,y,z) position is in sensor fenics range
        @reture:
            False: not
            True:  in
        @Modify:
            2021/08/31
        """
        if "plugin3D" in self.det_model:
            if (px < self.sx_l or px > self.sx_r
                or py < self.sy_l or py > self.sy_r):
                threeD_out_column=True
            else:
                threeD_out_column=False
        elif "planar3D" or "lgad3D" or "planarRing" in self.det_model:
            threeD_out_column=False
        return threeD_out_column
    
    def __del__(self):
        #for reuse of batch job?
        pass