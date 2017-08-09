import pysd
import pandas as pd


def create_static_test_matrix(model, filename=None):
    pass


def static_test_matrix(mdl_file, matrix=None, excel_file=None):
    if matrix:
        pass
    elif excel_file:
        matrix = pd.read_excel('SIR_Extreme_Conditions.xlsx', index_col=[0, 1])
    else:
        raise ValueError('Must supply a test matrix or refer to an external file')

    model = pysd.read_vensim(mdl_file)
    py_mdl_file = model.py_model_file

    errors = []
    for index, row in matrix.iterrows():
        try:
            model = pysd.load(py_mdl_file)
            result = model.run(params=dict([index]),
                               return_columns=row.index.values,
                               return_timestamps=0).loc[0]

            for key, value in row.items():
                if value != '-' and result[key] != value:
                    errors.append('When %s = %s, %s is %s instead of %s' %
                                  (index[0], index[1], key, result[key], value))

        except Exception as e:
            errors.append('When %s = %s, %s' %
                          (index[0], index[1], e))

    try:
        assert errors == []
    except:
        raise AssertionError(errors)


def create_range_test_matrix(model, filename=None):
    """
    Creates a test file that can be used to test that all model elements
    remain within their supported ranges.

    This supports replication of vensim's range checking functionality.

    If there are existing bounds listed in the model file, these will be incorporated.

    Parameters
    ----------
    model: PySD Model Object or
    filename

    Returns
    -------

    """

    def get_bounds(unit_string):
        parts = unit_string.split('[')
        return parts[-1].strip(']').split(',') if len(parts) > 1 else ['?', '?']

    docs = model.doc()
    docs['bounds'] = docs['Unit'].apply(get_bounds)
    docs['Min'] = docs['bounds'].apply(lambda x: float(x[0].replace('?', '-inf')))
    docs['Max'] = docs['bounds'].apply(lambda x: float(x[1].replace('?', '+inf')))

    output = docs[['Real Name', 'Comment', 'Unit', 'Min', 'Max']]

    if filename is None:
        return output
    elif filename.split('.')[-1] in ['xls', 'xlsx']:
        output.to_excel(filename, sheet_name='Bounds', index=False)
    elif filename.split('.')[-1] == 'csv':
        output.to_csv(filename, index=False)
    elif filename.split('.')[-1] == 'tab':
        output.to_csv(filename, sep='\t')
    else:
        raise ValueError('Unknown file extension %s' % filename.split('.')[-1])


def range_test(result, bounds=None, errors='return'):
    """
    Checks that the output of a simulation remains within the specified bounds.

    Parameters
    ----------
    result : pandas dataframe
        Probably the output of a PySD run, a pandas DF whose column names are specified
         as rows in the bounds matrix, and whose values will be tested for conformance to
         the bounds.

    bounds : test file name or test matrix

    errors : 'return' or 'raise'

    Raises
    ------
    AssertionError : When a parameter falls outside its support

    """

    if isinstance(bounds, pd.DataFrame):
        bounds = bounds.set_index('Real Name')
    elif isinstance(bounds, str):
        if bounds.split('.')[-1] in ['xls', 'xlsx']:
            bounds = pd.read_excel(bounds, sheetname='Bounds', index_col='Real Name')
        elif bounds.split('.')[-1] == 'csv':
            bounds = pd.read_csv(bounds, index_col='Real Name')
        elif bounds.split('.')[-1] == 'tab':
            bounds = pd.read_csv(bounds, sep='\t', index_col='Real Name')
        else:
            raise ValueError('Unknown file type: bounds')
    else:
        raise ValueError('Unknown type: bounds')

    error_list = []
    for colname in result.columns:
        if colname in bounds.index:
            lower_bound = bounds['Min'].loc[colname]
            below_bounds = result[colname] < lower_bound
            if any(below_bounds):
                error_list.append("'%s' below support %s at %s" % (
                    colname,
                    repr(lower_bound),
                    below_bounds[below_bounds].index.summary()))

            upper_bound = bounds['Max'].loc[colname]
            above_bounds = result[colname] > upper_bound
            if any(above_bounds):
                error_list.append("'%s' above support %s at %s" % (
                    colname,
                    repr(upper_bound),
                    above_bounds[above_bounds].index.summary()))

    if errors == 'return':
        return error_list
    elif errors == 'raise':
        raise AssertionError(error_list)
