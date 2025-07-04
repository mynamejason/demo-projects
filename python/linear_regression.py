from numpy import *

def compute_error(b, m, points):
    #initializing at 0
    totalError = 0

    for i in range(0, len(points)):
        #Get points x and y
        x = points[i, 0]
        y = points[i,1]

        #Get difference, square it, add it to the total
        totalError += (y - (m * x + b)) ** 2

    # Return the average of totalError and amount of points
    return totalError / float(len(points)) 

def step_gradient(b_current, m_current, points, learning_rate):
    # Initialize starting points for our gradients
    b_gradient = 0
    m_gradient = 0
    N = float(len(points))

    for i in range(0, len(points)):
        x = points[i, 0]
        y = points[i, 1]

        # direction with respect to b and m
        # computing partial derivatives of our error function
        # Partial derivatives allows us to update the 'direction' of where to meet the gradient descent
        b_gradient += -(2/N) * (y - ((m_current * x) + b_current))
        m_gradient += (2/N) * x * (y - ((m_current * x) + b_current))  
    
    # Update our b and m values using our partial derivatives
    new_b = b_current - (learning_rate * b_gradient)
    new_m = m_current - (learning_rate * m_gradient)

    return [new_b, new_m]

def gradient_descent_runner(points, starting_b, starting_m, learning_rate, num_iterations):
    # Get starting b and m
    b = starting_b
    m = starting_m

    # Gradient descent (gradient is another word for slope), an important concept in machine learning
    # Imagine a bowl and dropping a ball inside the bowl:
    # Gradient descent is like finding the lowest point in the bowl where the ball will stop moving;
    # the ball moving is representing the number of iterations before finding the lowest error (bottom of the bowl)
    for i in range(num_iterations):
        # Update b and m with the new (more accurate) b and m by performing this grandient step
        b, m = step_gradient(b, m, array(points), learning_rate)
    
    # Return optimal b and m
    return [b, m]

def run_main():
    
    # Step 1: Collect our data from a csv file
    points = genfromtxt('data.csv', delimiter=',')

    # Step 2: Define our hyperparameters: defining how our model is analyzing certain data
    learning_rate = 0.0001              # how fast should our model converge (grab the optimal result)?

    # y = mx + b (slope formula)
    initial_b = 0
    initial_m = 0

    num_iterations = 1000               # how much do we want to train this model? 

    # Step 3: Train our model
    # {[int]} represents variables that are initiated, which .format can insert into the string
    print('start gradient descent at b = {0}, m = {1}, error = {2}'.format(initial_b, initial_m, compute_error(initial_b, initial_m, points)))
    [b,m] = gradient_descent_runner(points, initial_b, initial_m, learning_rate, num_iterations)

    print('ending point at b = {0}, m = {1}, error = {2}'.format(num_iterations, b, m, compute_error(b, m, points)))

if __name__ == '__main__':
    run_main()