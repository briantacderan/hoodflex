from hoodflex.robb_modd._copp import DataFrameGenerator

class GradientProcessor(DataFrameGenerator):
    def __init__(self, ticker, start, date_points, **kwargs):
        super().__init__(ticker, start, date_points, **kwargs)
        self.x = DataFrameGenerator.get_X(self)
        self.y = DataFrameGenerator.get_Y(self)

    def get_b_gradient(self, b, m):
        N = len(self.x)
        difference = 0
        for i in range(N):
            x_val = self.x[i]
            y_val = self.y[i]
            difference += (y_val - ((m * x_val) + b))
        b_gradient = -(2 / N) * difference
        return b_gradient
    
    def get_m_gradient(self, b, m):
        N = len(self.x)
        difference = 0
        for i in range(N):
            x_val = self.x[i]
            y_val = self.y[i]
            difference += x_val * (y_val - ((m * x_val) + b))
        m_gradient = -(2 / N) * difference
        return m_gradient
    
class GradientIterator(GradientProcessor):
    def __init__(self, ticker, start, date_points, learning_rate=0.01, num_iterations=1000, **kwargs):
        super().__init__(ticker, start, date_points, **kwargs)
        self.learning_rate = learning_rate
        self.num_iterations = num_iterations

    def step_gradient(self, b, m):
        b_gradient = self.get_b_gradient(b, m)
        m_gradient = self.get_m_gradient(b, m)
        step_b = b - (self.learning_rate * b_gradient)
        step_m = m - (self.learning_rate * m_gradient)
        return [step_b, step_m]

    def optimize(self):
        b = 0
        m = 0
        for i in range(self.num_iterations):
            b, m = self.step_gradient(b, m)
        self.opt_slope = b
        self.opt_y_int = m
        return [b, m]
 