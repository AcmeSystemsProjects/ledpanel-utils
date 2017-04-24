#include <stdio.h>
#include <unistd.h>  // for sleep
#include <string.h>  // for memcpy
#include <signal.h>

#define SIZE 10240000

#define n_mod 3
#define w_panel 32

FILE *d = 0;

static volatile int loop = 1;

void intHandler(int dummy);

int main (int argc, const char **argv)
{
	FILE *f;
	
	signal(SIGINT, intHandler);

	if (argc > 1)
		f = fopen (argv[1], "rb");
	else
		f = fopen ("out.ppm", "rb");

	if (f) {
		static unsigned char b [SIZE];
		int n;
		
		if ((n = fread (b, sizeof(unsigned char), SIZE, f)) > 0) {
			char x1, x2;
			int  w, h, max;
			int offset;
			
			fclose (f); // close input file
			
			// read PPM header
			int x = sscanf ((char *)b, "%c%c\n%d %d\n%d\n%n", &x1, &x2, &w, &h, &max, &offset);
			if (x == 5) {
				fprintf (stderr, "rotateppm: Width: %d height: %d Max pixel value: %d\nrotateppm: Offset: %d\n", w, h, max, offset);
				
				// open device 
				d = fopen ("/sys/class/ledpanel/rgb_buffer", "wb");
				
				if (d) {
					fprintf (stderr, "rotateppm: read %d bytes\n", n);
					int w_panel_pixel = n_mod * w_panel;
					int x = 0;
					unsigned char blank[3] = {0};
					
					while (loop) {

						// copy data from file buffer to device
						unsigned char *p = b+offset; // skip header
						int r;

						for (r=0 ; r < 32; r++) {
							if (x < 0) {
								int a;
								for (a=0; a < -x; a++) fwrite (blank , sizeof(unsigned char), 3, d);
								int xx = x + w_panel_pixel;
								if (xx)
									fwrite (p, sizeof(unsigned char), xx * 3, d);
							} else
								fwrite (p+(x*3) , sizeof(unsigned char), w_panel_pixel * 3, d);
							
							p = p + (w*3);
						}
						fflush (d);
						// next column
						x++;
						// if the sliding window touches the end, go back
						// to the start
						if ((x + (w_panel_pixel)) > w) x = -(w_panel_pixel);
					}	
				} else {
					fprintf (stderr, "rotateppm: ledpanel device not found !\n");
				}
			} else {
				fprintf (stderr, "rotateppm: Unable to parse ppm file header\n");
			}
		}
		fclose (f);
	} else {
		fprintf (stderr, "rotateppm: bitmap file not found !\n");
		return 255;
	}
	// clean up panels
	if (d) {
		unsigned char blank[3] = {0};
		int r;
	
		for (r=0 ; r < 32; r++) {
			int c;
			for (c=0; c < (n_mod * w_panel); ++c) {
				fwrite (blank , sizeof(unsigned char), 3, d);
			}
		}
		fclose (d);
	}
	
	return 0;
}

void intHandler(int dummy)
{
	fprintf (stderr, "\nrotateppm: Interrupted by user.\n");
	loop = 0;
}
