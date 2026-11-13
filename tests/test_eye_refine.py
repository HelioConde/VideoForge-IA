"""Eyes should look calm at full closure, not like dark rectangular bars."""
import unittest
from videoforge import eye_refine


class NaturalBlinkTests(unittest.TestCase):
    W=128
    H=128

    def fixture(self):
        w,h=self.W,self.H
        original=bytearray(w*h*4)
        for y in range(h):
            for x in range(w):
                p=(y*w+x)*4
                original[p:p+4]=bytes((220+(x//40),125+(y//40),87+(x//50),255))
        # Two visible eyes, real color transfer from below eyelids.
        masks=[]
        for x1,x2,y1,y2 in ((26,56,35,46),(65,85,43,50)):
            mask=bytearray(w*h)
            for y in range(y1,y2):
                for x in range(x1,x2):
                    mask[y*w+x]=255
                    p=(y*w+x)*4
                    original[p:p+4]=bytes((43,21,20,255))
            masks.append(mask)
        curves=[
            {"points":[[26,37],[33,43],[44,45],[55,43]],
             "width":1.7,"color":[69,36,30]},
            {"points":[[66,45],[70,47],[79,50],[84,48]],
             "width":1.0,"color":[68,37,31]},
        ]
        return original,masks,curves

    def test_closed_eyelid_is_tapered_antialiased_and_uses_original_skin(self):
        original,masks,curves=self.fixture()
        head=bytearray(original)
        closed,qa=eye_refine.create_natural_blink(
            head,original,masks,[(39,66),(72,66)],curves,self.W,self.H)
        self.assertEqual(qa["eyes"],2)
        self.assertEqual(qa["external_model_calls"],0)
        self.assertIn("antialiased",qa["technique"])
        self.assertGreater(qa["healed_pixels"],len(masks)*100)
        self.assertGreater(qa["closed_lid_visible_pixels"],25)
        # Inside eye: painted cheek replaces dark iris, with gentle original variation.
        for x,y in ((39,40),(75,47)):
            p=(y*self.W+x)*4
            self.assertGreater(head[p],200)
            self.assertGreater(head[p+1],110)
            self.assertEqual(head[p+3],255)
        self.assertEqual(original[4*(40*self.W+39)],43) # original immutable
        alphas=closed[3::4]
        self.assertTrue(any(0<a<235 for a in alphas))
        self.assertLess(sum(a>0 for a in alphas),900)
        self.assertLess(max(alphas),256)

    def test_two_renders_deterministic_and_invalid_geometry_rejected(self):
        original,masks,curves=self.fixture()
        a=eye_refine.create_natural_blink(
            bytearray(original),original,masks,[(39,66),(72,66)],curves,self.W,self.H)
        b=eye_refine.create_natural_blink(
            bytearray(original),original,masks,[(39,66),(72,66)],curves,self.W,self.H)
        self.assertEqual(a,b)
        bad=[{"points":[[26,37],[33,43],[44,45],[55,43]],
              "width":12,"color":[69,36,30]},curves[1]]
        with self.assertRaisesRegex(eye_refine.EyeRefineError,"WIDTH_INVALID"):
            eye_refine.create_natural_blink(
                bytearray(original),original,masks,[(39,66),(72,66)],bad,self.W,self.H)
        with self.assertRaisesRegex(eye_refine.EyeRefineError,"COUNT_MISMATCH"):
            eye_refine.create_natural_blink(
                bytearray(original),original,masks,[(39,66),(72,66)],curves[:1],self.W,self.H)


if __name__=="__main__":
    unittest.main()
