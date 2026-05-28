import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import '../utils/constants.dart';

class ApiService {
  static Future<Map<String, dynamic>> uploadImages({
    required List<XFile> files,
    required String format,
    required int quality,
    required bool autoMode,

    required bool targetSizeEnabled,
    required int targetSizeKb,

    required bool resizeEnabled,
    required int resizeWidth,
    required int resizeHeight,
  }) async {
    var request = http.MultipartRequest(
      "POST",

      Uri.parse("${AppConstants.baseUrl}/upload"),
    );

    request.fields["format"] = format.toLowerCase();

    request.fields["quality"] = quality.toString();

    request.fields["auto_mode"] = autoMode.toString();

    request.fields["target_size_enabled"] = targetSizeEnabled.toString();

    request.fields["target_size_kb"] = targetSizeKb.toString();

    request.fields["resize_enabled"] = resizeEnabled.toString();

    request.fields["resize_width"] = resizeWidth.toString();

    request.fields["resize_height"] = resizeHeight.toString();

    for (var image in files) {
      var bytes = await image.readAsBytes();

      request.files.add(
        http.MultipartFile.fromBytes("files", bytes, filename: image.name),
      );
    }

    var response = await request.send();

    var responseBody = await response.stream.bytesToString();

    return jsonDecode(responseBody);
  }

  static Future<Map<String, dynamic>> getJobStatus(String jobId) async {
    final response = await http.get(
      Uri.parse("${AppConstants.baseUrl}/job/$jobId"),
    );

    return jsonDecode(response.body);
  }
}
