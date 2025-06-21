class Earthscii < Formula
  desc "Terminal-based 3D Earth terrain viewer"
  homepage "https://github.com/Kirito139/earthscii"
  url "https://github.com/Kirito139/earthscii/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "4737b318ac9a37240fa1d95f6ec7114467f195408163f8a0e2a7fb69e364bd4d"
  license "GPL-3.0-or-later"

  depends_on "python@3.11"
  depends_on "numpy"
  depends_on "rasterio"

  def install
    system "pip3", "install", "."
    bin.install_symlink libexec/"bin"/"earthscii"
  end

  test do
    system "earthscii", "--help"
  end
end
