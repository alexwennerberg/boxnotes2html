from boxnotes2html.table import Table


class TestTable:
    
    def test_render_markdown(self):
        table = Table()
        table.add_data(1, 1, "Name")
        table.add_data(1, 2, "Country")
        table.add_data(1, 3, "Birthdate")
        
        table.add_data(2, 1, "Jill")
        table.add_data(2, 2, "Australia")
        table.add_data(2, 3, "2000-01-01")
        
        table.add_data(3, 1, "Alfonse")
        table.add_data(3, 2, "Chile")
        table.add_data(3, 3, "1981-02-04")
        
        expected = "| Name | Country | Birthdate |\n" + \
            "| :-- | :-- | :-- |\n" + \
            "| Jill | Australia | 2000-01-01 |\n" + \
            "| Alfonse | Chile | 1981-02-04 |\n"
        
        assert table.render_markdown() == expected
    
    def test_append_data_markdown(self):
        """
        Test that appending data to add_data works as expected and renders multiple lines properly.
        """
        table = Table()
        table.add_data(1, 1, "Name")
        table.add_data(1, 1, "(Full name)")
        table.add_data(1, 1, "(but with no spaces)")
        table.add_data(1, 1, "(as in full name camelcase)")
        
        table.add_data(2, 1, "JillFromDownUnder")
        
        expected = "| Name<br>(Full name)<br>(but with no spaces)<br>(as in full name camelcase) |\n" + \
            "| :-- |\n" + \
            "| JillFromDownUnder |\n"
        
        assert table.render_markdown() == expected
