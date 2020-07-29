# -*- coding: utf-8 -*-
"""
Generate markdown tables programmatically.
"""


class Table:
    matrix = {}
    
    def __init__(self):
        self.matrix = {}

    def render_markdown(self):
        """
        Render the table as markdown
        """
        out = []
        headers = 0
        for row_key, col in self.matrix.items():
            for cell_key, cell in col.items():
                if headers is not False:
                    headers += 1
                out.append(f"| {cell} ")
            
            out.append("|\n")
            
            if headers is not False and headers > 0:
                out.append("| :-- " * headers)
                out.append("|\n")
                headers = False
        
        return "".join(out)

    def add_data(self, row, cell, data):
        if row not in self.matrix:
            self.matrix[row] = {}
        
        quoted = data.replace("\n", "<br>")
        
        if cell in self.matrix[row]:
            self.matrix[row][cell] += f"<br>{quoted}"
        else:
            self.matrix[row][cell] = quoted
