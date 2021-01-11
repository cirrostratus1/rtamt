#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include <boost/python/module.hpp>
#include <boost/python/wrapper.hpp>

#include <rtamt_stl_library/stl_since_bounded_node.h>

using namespace boost::python;
using namespace stl_library;

BOOST_PYTHON_MODULE(stl_since_bounded_node)
{
    class_<StlSinceBoundedNode>("SinceBoundedOperation", init<int,int>())
        .def("update", static_cast<double (StlSinceBoundedNode::*)(double, double)>(&StlSinceBoundedNode::update))
        .def("reset", &StlSinceBoundedNode::reset)
    ;
}