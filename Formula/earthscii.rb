class Earthscii < Formula
  desc "Terminal-based 3D Earth terrain viewer"
  homepage "https://github.com/Kirito139/earthscii"
  url "https://github.com/Kirito139/earthscii/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "c7839386b7e980ab0f1fbf22bb10616a2967f601b8133af30bf024ba1fd6bdf4"
  license "GPL-3.0-or-later"

  depends_on "python@3.11"
  depends_on "numpy"
  depends_on "rasterio"

  def install
    ENV["PIP_BREAK_SYSTEM_PACKAGES"] = "1"
    system "pip3", "install", ".", "--prefix=#{prefix}"
  end

  test do
    system "earthscii", "--help"
  end
end
