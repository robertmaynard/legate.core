#include "hello_world.h"
#include "legate_library.h"

namespace hello {

class SumTask : public Task<SumTask, SUM> {
 public:
  static void cpu_variant(legate::TaskContext& context)
  {
    legate::Store& input        = context.inputs()[0];
    legate::Rect<1> input_shape = input.shape<1>();  // should be a 1-Dim array
    auto in                     = input.read_accessor<float, 1>();

    logger.info() << "Sum [" << input_shape.lo << "," << input_shape.hi << "]";

    float total = 0;
    // i is a global index for the complete array
    for (size_t i = input_shape.lo; i <= input_shape.hi; ++i) { total += in[i]; }

    /**
      The task launch as a whole will return a single value (Store of size 1)
      to the caller. However, each point task gets a separate Store of the
      same size as the result, to reduce into. This "local accumulator" will
      be initialized by the runtime, and all we need to do is call .reduce()
      to add our local contribution. After all point tasks return, the runtime
      will make sure to combine all their buffers into the single final result.
    */
    using Reduce          = Legion::SumReduction<float>;
    legate::Store& output = context.reductions()[0];
    auto sum              = output.reduce_accessor<Reduce, true, 1>();
    // Best-practice is to validate types
    assert(output.code() == FLOAT_LT);
    assert(output.dim() == 1);
    assert(output.shape<1>() == legate::Rect<1>(0, 0));
    sum.reduce(0, total);
  }
};

}  // namespace hello

namespace  // unnamed
{

static void __attribute__((constructor)) register_tasks(void)
{
  hello::SumTask::register_variants();
}

}  // namespace
