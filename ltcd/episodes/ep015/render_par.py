"""parallel render helper: python render_par.py N  -> renders day015.mp4 using N worker processes."""
import sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
if len(sys.argv) > 2 and sys.argv[1] == "--chunk":
    a, b, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    sys.argv = [sys.argv[0]]
    sys.path.insert(0, HERE); import episode as E
    import ltcd as L, cairo
    E.S.build()
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, L.W, L.H)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{L.W}x{L.H}",
                           "-r", str(L.FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out],
                          stdin=subprocess.PIPE)
    for f in range(a, b):
        L.render_frame(f / L.FPS, surf); surf.flush(); ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close(); ff.wait(); sys.exit(0)
n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
sys.argv = [sys.argv[0]]
sys.path.insert(0, HERE); import episode as E
import ltcd as L
dur = E.S.build(); NF = L.NFRAMES
L.synth_audio("mix.wav")
cuts = [NF * i // n for i in range(n + 1)]
procs = [subprocess.Popen([sys.executable, __file__, "--chunk", str(cuts[i]), str(cuts[i + 1]), f"part{i}.mp4"]) for i in range(n)]
for p in procs: p.wait()
with open("parts.txt", "w") as fh:
    for i in range(n): fh.write(f"file 'part{i}.mp4'\n")
subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "parts.txt", "-i", "mix.wav",
                       "-c:v", "copy", "-ar", "48000", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", "day015.mp4"])
for i in range(n): os.remove(f"part{i}.mp4")
os.remove("parts.txt")
print("done day015.mp4", NF, "frames")
