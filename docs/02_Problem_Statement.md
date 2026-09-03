# Problem Statement

Livestock keepers and students of animal husbandry rely on visual observation to notice reduced movement, prolonged recumbency, or unusual gait. When many animals share a yard or shed, continuous observation is difficult. Missed cues can delay inspection even when the cause is simple (lameness, isolation, heat stress, or injury).

Existing commercial farm systems often assume dedicated cameras, RFID, or paid cloud services. College laboratories typically have only a laptop, a webcam, and public-domain photos or short videos.

**Problem:** There is a need for an understandable, hardware-free computer-vision application that can:

1. Detect cattle in user-supplied images and videos.
2. Maintain approximate animal identities during a clip.
3. Summarise simple visible behaviours.
4. Raise an early-warning flag when activity looks unusual.
5. Present results on a professional dashboard for demonstration and review.

**Constraints:** The solution must not claim disease diagnosis, must fail clearly if the AI model is missing, must remain usable with uploads when no camera is present, and must be implementable as a student MVP.
