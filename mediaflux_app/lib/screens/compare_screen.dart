import 'package:flutter/material.dart';

class CompareScreen extends StatefulWidget {
  final String originalUrl;

  final String optimizedUrl;

  const CompareScreen({
    super.key,

    required this.originalUrl,

    required this.optimizedUrl,
  });

  @override
  State<CompareScreen> createState() => _CompareScreenState();
}

class _CompareScreenState extends State<CompareScreen> {
  double sliderValue = 0.5;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,

      appBar: AppBar(
        backgroundColor: Colors.black,

        elevation: 0,

        title: const Text("Before / After Compare"),
      ),

      body: LayoutBuilder(
        builder: (context, constraints) {
          return Column(
            children: [
              Expanded(
                child: Stack(
                  children: [
                    Positioned.fill(
                      child: Image.network(
                        widget.optimizedUrl,

                        fit: BoxFit.cover,

                        alignment: Alignment.center,

                        loadingBuilder: (context, child, progress) {
                          if (progress == null) {
                            return child;
                          }

                          return const Center(
                            child: CircularProgressIndicator(
                              color: Colors.deepPurpleAccent,
                            ),
                          );
                        },

                        errorBuilder: (context, error, stackTrace) {
                          return const Center(
                            child: Icon(
                              Icons.broken_image,

                              color: Colors.redAccent,

                              size: 60,
                            ),
                          );
                        },
                      ),
                    ),

                    Positioned.fill(
                      child: ClipRect(
                        clipper: CompareClipper(sliderValue),

                        child: Image.network(
                          widget.originalUrl,

                          fit: BoxFit.cover,

                          alignment: Alignment.center,

                          loadingBuilder: (context, child, progress) {
                            if (progress == null) {
                              return child;
                            }

                            return const Center(
                              child: CircularProgressIndicator(
                                color: Colors.deepPurpleAccent,
                              ),
                            );
                          },

                          errorBuilder: (context, error, stackTrace) {
                            return const Center(
                              child: Icon(
                                Icons.broken_image,

                                color: Colors.redAccent,

                                size: 60,
                              ),
                            );
                          },
                        ),
                      ),
                    ),

                    Positioned(
                      left: constraints.maxWidth * sliderValue,

                      top: 0,

                      bottom: 0,

                      child: Container(
                        width: 3,

                        color: Colors.deepPurpleAccent,
                      ),
                    ),
                  ],
                ),
              ),

              Padding(
                padding: const EdgeInsets.all(20),

                child: Slider(
                  value: sliderValue,

                  activeColor: Colors.deepPurpleAccent,

                  onChanged: (value) {
                    setState(() {
                      sliderValue = value;
                    });
                  },
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class CompareClipper extends CustomClipper<Rect> {
  final double sliderValue;

  CompareClipper(this.sliderValue);

  @override
  Rect getClip(Size size) {
    return Rect.fromLTRB(0, 0, size.width * sliderValue, size.height);
  }

  @override
  bool shouldReclip(CompareClipper oldClipper) {
    return oldClipper.sliderValue != sliderValue;
  }
}
