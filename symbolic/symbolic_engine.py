import ast
import numbers
from z3 import *

# Remarks z3
# Power ** has to be with Real
# Modulo % has to be with Int

# questions:
# - py_sim.py line 53
# - 'x': None ok? model_completion, None values?

# Command line: export PYTHONPATH=$PYTHONPATH:/Users/rikmelis/Desktop/Z3HOME/bin in .bash_profile


class SymbolicEngine:
    def __init__(self, function_name, program_ast):
        self.function = find_function(program_ast, function_name)
        self.program_ast = program_ast

    # TODO: implement symbolic execution
    # The return value is a list of tuples [(input#1, ret#1), ...]
    # where input is a dictionary specifying concrete value used as input, e.g. {'x': 1, 'y': 2}
    # and ret is expected return value of the function
    # Note: all returned inputs should explore different program paths
    def explore(self):
        inputs = generate_inputs(self.function)
        # start_state is a tuple with the input variables (with assignments) and a list of all the constraints at that point
        start_state = (inputs, [])
        f = FunctionEvaluator(self.function, self.program_ast, start_state)  
        input_to_ret = f.get_input_to_ret()
        assertion_violations_to_input = f.violated_assertions
        return (input_to_ret, assertion_violations_to_input)


###############
# Interpreter #
###############

def run_expr(expr, f, state = (None, None)):
    if type(expr) == ast.Tuple:
        rs = [(state[1], [])]
        for el in expr.elts: 
            rs = [(constraints, r[1] + [value])
                for r in rs for (_, constraints, value) in run_expr(el, f, (state[0], r[0]))]
        rs = [(state[0], r[0], tuple(r[1])) for r in rs]
        return rs
        
    if type(expr) == ast.Name:
        if expr.id == 'True':
            return [(state[0], state[1], True)]
        elif expr.id == 'False':
            return [(state[0], state[1], False)]
        return [(state[0], state[1], state[0][expr.id])]
        
    if type(expr) == ast.Num:
        assert (isinstance(expr.n, numbers.Integral))
        return [(state[0], state[1], expr.n)]

    if type(expr) == ast.BinOp:
        rs = []
        for (assignments1, constraints1, e1) in run_expr(expr.left, f, state):
            for (assignments2, constraints2, e2) in run_expr(expr.right, f, (assignments1, constraints1)):
                if type(expr.op) == ast.Add:
                    rs.append((assignments2, constraints2, e1 + e2))
                if type(expr.op) == ast.Sub:
                    rs.append((assignments2, constraints2, e1 - e2))
                if type(expr.op) == ast.Mult:
                    rs.append((assignments2, constraints2, e1 * e2))
                if type(expr.op) == ast.Div:
                    rs.append((assignments2, constraints2, e1 / e2))
                if type(expr.op) == ast.Mod:
                    rs.append((assignments2, constraints2, e1 % e2))
                if type(expr.op) == ast.Pow:
                    rs.append((assignments2, constraints2, e1 ** e2))
                # Evaluate only with constants
                if type(expr.op) == ast.LShift and type(expr.left) == ast.Num and type(expr.right) == ast.Num:
                    rs.append((assignments2, constraints2, e1 << e2))
                if type(expr.op) == ast.RShift and type(expr.left) == ast.Num and type(expr.right) == ast.Num:
                    rs.append((assignments2, constraints2, e1 >> e2))
        return rs

    if type(expr) == ast.UnaryOp:
        rs = []
        for (assignments, constraints, e) in run_expr(expr.operand, f, state):
            if type(expr.op) == ast.Not:
                rs.append((assignments, constraints, Not(e)))
            if type(expr.op) == ast.USub:
                rs.append((assignments, constraints, -e))
        return rs

    if type(expr) == ast.Compare:
        assert (len(expr.ops) == 1)  # Do not allow for x==y==0 syntax
        assert (len(expr.comparators) == 1)
        op = expr.ops[0]
        rs = []
        for (assignments1, constraints1, e1) in run_expr(expr.left, f, state):
            for (assignments2, constraints2, e2) in run_expr(expr.comparators[0], f, (assignments1, constraints1)):
                if type(op) == ast.Eq:
                    rs.append((assignments2, constraints2, e1 == e2))
                if type(op) == ast.NotEq:
                    rs.append((assignments2, constraints2, e1 != e2))
                if type(op) == ast.Gt:
                    rs.append((assignments2, constraints2, e1 > e2))
                if type(op) == ast.GtE:
                    rs.append((assignments2, constraints2, e1 >= e2))
                if type(op) == ast.Lt:
                    rs.append((assignments2, constraints2, e1 < e2))
                if type(op) == ast.LtE:
                    rs.append((assignments2, constraints2, e1 <= e2))
        return rs

    if type(expr) == ast.BoolOp:
        if type(expr.op) == ast.And:
            rs = [(state[1], True)]
            for v in expr.values:
                rs = [(constraints, And(r[1], value))
                    for r in rs for (_, constraints, value) in run_expr(v, f, (state[0], r[0]))]
            rs = [(state[0], r[0], r[1]) for r in rs]
            return rs
        if type(expr.op) == ast.Or:
            rs = [(state[1], False)]
            for v in expr.values:
                rs = [(constraints, Or(r[1], value))
                    for r in rs for (_, constraints, value) in run_expr(v, f, (state[0], r[0]))]
            rs = [(state[0], r[0], r[1]) for r in rs]
            return rs

    if type(expr) == ast.Call:
        function = find_function(f.program_ast, expr.func.id)
        assert (len(expr.args) == len(function.args.args))
        
        start_states = [(({}, state[1]))]
        for i in range(0, len(expr.args)):
            start_states = [(dict(s[0].items() + {function.args.args[i].id : value}.items()), constraints)
                for s in start_states for (_, constraints, value) in run_expr(expr.args[i], f, (state[0], s[1]))]

        paths = []
        for start_state in start_states:
            f1 = FunctionEvaluator(function, f.program_ast, start_state, f.main_f)
            paths += f1.get_paths()
        paths = [(state[0], constraints, return_value) for (assignments, constraints, return_value) in paths]
        return paths
        
    raise Exception('Unhandled expression: ' + ast.dump(expr))
                                                              
def run_stmt(stmt, f, state):                                 
    if type(stmt) == ast.Return:
        f.paths += run_expr(stmt.value, f, state)
        return []                                             
                                                              
    if type(stmt) == ast.If:                                      
        new_states = []
        for (assignments, constraints, cond) in run_expr(stmt.test, f, state):
            ifState = (assignments, constraints + [cond])               
            elseState = (assignments, constraints + [Not(cond)])    
            new_states_if = run_body(stmt.body, f, ifState)
            if len(stmt.orelse) > 0:                              
                new_states_if += run_body(stmt.orelse, f, elseState) 
            elif len(new_states_if) == 0:
                new_states_if = [elseState]
            new_states += new_states_if
        return new_states                                     
                                                              
    if type(stmt) == ast.Assign:                              
        assert (len(stmt.targets) == 1)  # Disallow a=b=c syntax
        lhs = stmt.targets[0]                                         
        new_states = []
        for (assignments, constraints, rhs) in run_expr(stmt.value, f, state):
            assign = assignments.copy()
            if type(lhs) == ast.Tuple:                            
                assert (type(rhs) == tuple)                       
                assert (len(rhs) == len(lhs.elts))                
                for el_index in range(len(lhs.elts)):             
                    el = lhs.elts[el_index]                       
                    assert (type(el) == ast.Name)                 
                    assign[el.id] = rhs[el_index]            
                new_states.append((assign, constraints))                               
            if type(lhs) == ast.Name:        
                assign[lhs.id] = rhs
                new_states.append((assign, constraints))
        return new_states
        
    if type(stmt) == ast.Assert:
        if stmt not in f.main_f.violated_assertions:
            # TODO: implement check whether the assertion holds.
            # However do not throw exception in case the assertion does not hold.
            # Instead return inputs that trigger the violation from SymbolicEngine.explore()
            for (assignments, constraints, cond) in run_expr(stmt.test, f, state):
                s = Solver()
                s.add(constraints)
                s.add(Not(cond))
                if s.check() == z3.sat:
                    m = s.model()
                    f.main_f.violated_assertions[stmt] = {key : m[val] if m[val] 
                        is not None else 0 for key,val in f.main_f.start_state[0].items()}
                    return [state]
        return [state]
                                                              
    raise Exception('Unhandled statement: ' + ast.dump(stmt)) 
                             
def run_body(body, f, state):
    states = [state]
    for stmt in body:
        new_states = []
        for state in states:
            new_states += run_stmt(stmt, f, state)
        states = new_states
    return states
                                                              
class FunctionEvaluator:                                      
    def __init__(self, function, program_ast, start_state, main_f = None):
        if main_f == None:
            main_f = self
                   
        assert (type(function) == ast.FunctionDef)
        for arg in function.args.args:
            assert arg.id in start_state[0]

        self.function = function
        self.program_ast = program_ast
        self.start_state = start_state
        self.main_f = main_f
        # paths is a list of tuples of 3 elements: (input variables, constraints, return value). each tuple gives one possible execution path      
        self.paths = []
        self.violated_assertions = {}

    def get_paths(self):
        run_body(self.function.body, self, self.start_state)
        return self.paths
    
    def get_input_to_ret(self):
        input_to_ret = []
        for (_, constraints, ret) in self.get_paths():
            s = Solver()
            s.add(constraints)
            if s.check() == z3.sat:           
                m = s.model()
                return_value = get_return_value(ret, m)
                # take 0 if m[val] is None (its value doesn't matter in this case)
                input_to_ret.append(({key : m[val] if m[val] is not None else 0 
                    for key,val in self.start_state[0].items()}, return_value))
        return input_to_ret

####################
# Helper Functions #
####################

# f: function for which to generate inputs
# inputs: dictionary that maps argument names to values. e.g. {'x': 42 }
def generate_inputs(f):
    for arg in f.args.args:
        assert (type(arg) == ast.Name)
    return {arg.id: Int(arg.id + "0") for arg in f.args.args}

def find_function(p, function_name):
    assert (type(p) == ast.Module)
    for x in p.body:
        if type(x) == ast.FunctionDef and x.name == function_name:
            return x
    raise LookupError('Function %s not found' % function_name)

def get_return_value(ret, m):
    if isinstance(ret, int) or isinstance(ret, bool): 
        return ret
    else:
        return_value = m.eval(ret, model_completion=True)
        if is_int_value(return_value):
            return_value = return_value.as_long()
        else:
            return_value = is_true(return_value)
        return return_value