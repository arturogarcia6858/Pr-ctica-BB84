import numpy as np

class GolayCode:
    def __init__(self):
        """
        k: Length of message
        n: Length of codeword 
        - Here empty instances of the generator matrix, parity check matrix
        and B matrix are created to make them accessible throughout 
        the class and to return them without having to call the function.
        """
        self.k = 12
        self.n = 24

        # Generate empty instances just to have them accessible in the class.
        self.b_mat = []
        self.generator_mat = []
        self.parity_check = []

    def b_matrix(self):

        self.b_mat = np.array([
            [1,1,0,1,1,1,0,0,0,1,0,1],
            [1,0,1,1,1,0,0,0,1,0,1,1],
            [0,1,1,1,0,0,0,1,0,1,1,1],
            [1,1,1,0,0,0,1,0,1,1,0,1],
            [1,1,0,0,0,1,0,1,1,0,1,1],
            [1,0,0,0,1,0,1,1,0,1,1,1],
            [0,0,0,1,0,1,1,0,1,1,1,1],
            [0,0,1,0,1,1,0,1,1,1,0,1],
            [0,1,0,1,1,0,1,1,1,0,0,1],
            [1,0,1,1,0,1,1,1,0,0,0,1],
            [0,1,1,0,1,1,1,0,0,0,1,1],
            [1,1,1,1,1,1,1,1,1,1,1,0]
        ])

        return self.b_mat


    def generator_matrix(self):
        """
        - binary Golay code generator matrix from 
        https://www.maplesoft.com/applications/Preview.aspx?id=1757
        """

        self.generator_mat = np.zeros((self.n, self.n-self.k), dtype=int)
        # self.generator_mat[:self.k, :] = self.b_matrix()
        # self.generator_mat[self.k:, :] = np.identity(self.n-self.k, dtype=int)
        self.generator_mat[:self.k, :] = np.identity(self.n-self.k, dtype=int) 
        self.generator_mat[self.k:, :] = self.b_matrix()
        return self.generator_mat

    def parity_check_matrix(self):

        self.parity_check = np.zeros((self.n, self.n-self.k), dtype=int)
        # self.parity_check[:self.k, :] = np.identity(self.n-self.k, dtype=int)
        # self.parity_check[self.k:, :] = self.b_matrix()
        self.parity_check[:self.k, :] = self.b_matrix()
        self.parity_check[self.k:, :] = np.identity(self.n-self.k, dtype=int)
        return self.parity_check

    def get_generator_matrix(self):

        if len(self.generator_mat) == 0:
            self.generator_mat = self.generator_matrix()

        return self.generator_mat

    def get_parity_check_matrix(self):
        if len(self.parity_check) == 0:
            self.parity_check = self.parity_check_matrix()

        return self.parity_check

    def get_b_matrix(self):
        if len(self.b_mat) == 0:
            self.b_mat = self.b_matrix()

        return self.b_mat

