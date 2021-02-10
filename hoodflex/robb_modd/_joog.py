from hoodflex.robb_modd._copp import DataFrameGenerator

class GradientProcessor(DataFrameGenerator):
    def __init__(self, ticker, date_points, **kwargs):
        super().__init__(ticker, date_points, **kwargs)
        self.x = self.get_X()
        self.y = self.get_Y()

    def get_b_gradient(self, b, m):
        N = len(self.edit_X)
        difference = 0
        for i in range(N):
            x_val = self.edit_X[i]
            y_val = self.edit_Y[i]
            difference += (y_val - ((m * x_val) + b))
        b_gradient = -(2 / N) * difference
        return b_gradient
    
    def get_m_gradient(self, b, m):
        N = len(self.edit_x)
        difference = 0
        for i in range(N):
            x_val = self.edit_x[i]
            y_val = self.edit_y[i]
            difference += x_val * (y_val - ((m * x_val) + b))
        m_gradient = -(2 / N) * difference
        return m_gradient
    
class GradientIterator(GradientProcessor):
    def __init__(self, ticker, date_points, learning_rate=0.01, num_iterations=1000, **kwargs):
        super().__init__(ticker, date_points, **kwargs)
        self.learning_rate = learning_rate
        self.num_iterations = num_iterations

    def step_gradient(self, b, m):
        b_gradient = self.get_b_gradient(b, m)
        m_gradient = self.get_m_gradient(b, m)
        step_b = b - (self.learning_rate * b_gradient)
        step_m = m - (self.learning_rate * m_gradient)
        return [step_b, step_m]

    def optimize(self): 
        self.edit_x = self.x.pop(0)
        self.edit_y = self.y.pop(0)
        self.edit_x.append(self.edit_x[-1]+0.01)
        self.edit_x.append(self.edit_y[-1]+0.01)
        b = 0
        m = 0
        for i in range(self.num_iterations):
            b, m = self.step_gradient(b, m)
        self.opt_b = b
        self.opt_m = m
 