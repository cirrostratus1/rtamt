/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include <boost/python/module.hpp>
#include <boost/python/wrapper.hpp>

#include <rtamt_stl_library/stl_historically_bounded_node.h>

using namespace boost::python;
using namespace stl_library;

BOOST_PYTHON_MODULE(stl_historically_bounded_node)
{
    class_<StlHistoricallyBoundedNode>("HistoricallyBoundedOperation", init<int,int>())
        .def("update", static_cast<double (StlHistoricallyBoundedNode::*)(double)>(&StlHistoricallyBoundedNode::update))
        .def("reset", &StlHistoricallyBoundedNode::reset)
    ;
}