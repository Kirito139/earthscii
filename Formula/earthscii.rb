class Earthscii < Formula
  desc "Terminal-based 3D Earth terrain viewer"
  homepage "https://github.com/Kirito139/earthscii"
  url "https://github.com/Kirito139/earthscii/archive/refs/tags/v0.1.1.tar.gz"
  sha256 "17ac2aaee665fc10d49748adfc6c3b75ce5801827e997296fd1e4ed9b0723af1"
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
