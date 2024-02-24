// Copyright (c) 2022, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#ifndef CRS4_NUMPY_H_
#define CRS4_NUMPY_H_

#include "dali/pipeline/data/tensor.h"
#include "dali/core/stream.h"

using namespace dali;

namespace crs4 {

  DLL_PUBLIC Tensor<CPUBackend> NewReadTensor(InputStream *src, bool pinned);

}  // namespace crs4

#endif  // CRS4_NUMPY_H_
