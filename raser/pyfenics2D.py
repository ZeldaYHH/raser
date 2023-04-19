# -*- encoding: utf-8 -*-

import fenics
import mshr



class FenicsCal2D:
    def __init__(self,my_d,fen_dic):
        self.det_model = fen_dic['det_model']
        self.fl_x=my_d.l_x
        self.fl_y=my_d.l_y
        self.fl_z=my_d.l_z

        self.tol = 1e-14
        self.bias_voltage = my_d.voltage

        self.striplenth=fen_dic["striplenth"]
        self.elelenth=fen_dic["elelenth"]
        self.tol_elenumber=int(fen_dic["tol_elenumber"])
        
        self.generate_mesh(my_d,fen_dic['mesh'])
        self.V = fenics.FunctionSpace(self.mesh2D, 'P', 1)
        self.u_bc = self.boundary_definition(my_d)
        self.electric_field(my_d)
        self.u_w_bc=[]
        for elenumber in range(self.tol_elenumber):
            if (elenumber<my_d.l_x/self.striplenth):
                self.u_w_bc.append(self.boundary_definition_w_p(my_d,elenumber))
            else:
                self.u_w_bc.append(self.boundary_definition_p_w_p(my_d))
        self.weighting_potential(my_d)
        


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

        if "planar" in self.det_model :
            m_sensor = mshr.Rectangle(fenics.Point(0, 0), 
                                fenics.Point(self.fl_x, self.fl_z))
            self.mesh2D = mshr.generate_mesh(m_sensor,mesh_number)


    def boundary_definition(self,my_d):
        if "planar" in self.det_model:
            u_bc_l = self.boundary_definition_planar(my_d,my_d.voltage,0.0)
            pass
        else:
            raise NameError(self.det_model)

        return u_bc_l

    def boundary_definition_p_w_p(self,my_d):
        if "planar" in self.det_model:
            u_bc_l = self.boundary_definition_planar(my_d,1.0,0.0)
            pass
        else:
            raise NameError(self.det_model)

        return u_bc_l


    def boundary_definition_planar(self,my_d,p_ele,n_ele):
        """
        @description:
            Get boundary definition of planar detector with Possion and Laplace equations
        @Modify:
            2021/08/31
        """
        u_D = fenics.Expression('x[1]<tol ? p_1:p_2',
                                degree = 2, tol = 1E-14,
                                p_1 = p_ele, p_2 = n_ele)

        def boundary(x, on_boundary):
            return abs(x[1])<self.tol or abs(x[1]-self.fl_z)<self.tol
        bc_l = fenics.DirichletBC(self.V, u_D, boundary)
        return bc_l
    
    def boundary_definition_w_p(self,my_d,elenumber):
        if "planar" in self.det_model:
            u_w_bc_l = self.boundary_definition_strip(my_d,1.0,0.0,elenumber)
    
            pass
        else:
            raise NameError(self.det_model)

        return  u_w_bc_l

    def boundary_definition_strip(self,my_d,p_ele,n_ele,elenumber):
        u_D = fenics.Expression('(x[1]<tol && x[0]>xstripl && x[0]<xstripr) ? p_1:p_2',
                                degree = 2, tol = 1E-14,xstripl=self.striplenth*elenumber,
                                xstripr=self.striplenth*elenumber+self.elelenth,z=self.fl_z,
                                p_1 = p_ele, p_2 = n_ele)

        def boundary(x, on_boundary):
            return ((abs(x[1])<self.tol and 
                        x[0]>self.striplenth*elenumber+self.tol and
                      x[0]<self.striplenth*elenumber+self.elelenth+self.tol)
                    or (abs(x[1]-self.fl_z)<self.tol))
        bc_l = fenics.DirichletBC(self.V, u_D, boundary)
        return bc_l

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
        W = fenics.VectorFunctionSpace(self.mesh2D, 'P', 1)
        self.grad_u = fenics.project(fenics.as_vector((self.u.dx(0),
                                                       self.u.dx(1))),W)
        
    
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
        f = fenics.Constant(e0*my_d.d_neff*1e6/perm0/perm_mat)
        return f
        

   
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
        
        try:
            f_p = self.u(px,pz)
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
        
        try:
            x_value,z_value = self.grad_u(px,pz)
            x_value = x_value* -1
            y_value = 0
            z_value = z_value* -1
        except RuntimeError:
            x_value,y_value,z_value = 0,0,0
        
        return x_value,y_value,z_value
    
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
        self.u_w=[]
        for elenumber in range(self.tol_elenumber):
            self.u_w.append(fenics.Function(self.V))
            fenics.solve(a_w == L_w, self.u_w[elenumber], self.u_w_bc[elenumber])
        

        

    def get_w_p(self,px,py,pz,elenumber):
        self.elenumber=elenumber
        try:
            f_w_p = self.u_w[elenumber](px,pz)
        except RuntimeError:
            f_w_p = 0.0
        return f_w_p

    def __del__(self):
        #for reuse of batch job?
        pass
