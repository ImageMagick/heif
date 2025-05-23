/*
 * HEIF codec.
 * Copyright (c) 2024 Dirk Farin <dirk.farin@gmail.com>
 *
 * This file is part of libheif.
 *
 * libheif is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version.
 *
 * libheif is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with libheif.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "security_limits.h"
#include <limits>


struct heif_security_limits global_security_limits {
    1,

    // --- version 1

    // Artificial limit to avoid allocating too much memory.
    // 32768^2 = 1.5 GB as YUV-4:2:0 or 4 GB as RGB32
    32768 * 32768,
    4096 * 4096,
    16*16,
    1000,

    100 * 1024 * 1024, // 100 MB
    512 * 1024 * 1024,  // 512 MB

    256,
    32,
    64,

    100
};


struct heif_security_limits disabled_security_limits{
        1
};


Error check_for_valid_image_size(const heif_security_limits* limits, uint32_t width, uint32_t height)
{
  uint64_t maximum_image_size_limit = limits->max_image_size_pixels;

  // --- check whether the image size is "too large"

  if (maximum_image_size_limit > 0) {
    auto max_width_height = static_cast<uint32_t>(std::numeric_limits<int>::max());
    if ((width > max_width_height || height > max_width_height) ||
        (height != 0 && width > maximum_image_size_limit / height)) {
      std::stringstream sstr;
      sstr << "Image size " << width << "x" << height << " exceeds the maximum image size "
           << maximum_image_size_limit << "\n";

      return {heif_error_Memory_allocation_error,
              heif_suberror_Security_limit_exceeded,
              sstr.str()};
    }
  }

  if (width == 0 || height == 0) {
    return {heif_error_Memory_allocation_error,
            heif_suberror_Invalid_image_size,
            "zero width or height"};
  }

  return Error::Ok;
}
